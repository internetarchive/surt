# Copyright(c)2012-2013 Internet Archive. Software license AGPL version 3.
#
# This file is part of the `surt` python package.
#
#     surt is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     surt is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with surt.  If not, see <http://www.gnu.org/licenses/>.
#
#     The surt source is hosted at https://github.com/internetarchive/surt

import re
import struct
import socket
import encodings.idna

from .handyurl import handyurl

try:
    from urllib.parse import quote_from_bytes, unquote_to_bytes
except:
    from urllib import quote as quote_from_bytes, unquote as unquote_to_bytes

__all__ = [
    'DefaultIAURLCanonicalizer',
    'GoogleURLCanonicalizer',
    'IAURLCanonicalizer'
    ]

def normalizePath(path):
    if not path:
        return b'/'

    #gives an empty trailing element if path ends with '/':
    paths       = path.split(b'/')
    keptPaths   = []
    first       = True

    for p in paths:
        if first:
            first = False
            continue
        elif b'.' == p:
            # skip
            continue
        elif b'..' == p:
            #pop the last path, if present:
            if len(keptPaths) > 0:
                keptPaths = keptPaths[:-1]
            else:
                # TODO: leave it? let's do for now...
                keptPaths.append(p)
        else:
            keptPaths.append(p)

    path = b'/'

    # If the path ends in '/', then the last element of keptPaths will be ''
    # Since we add a trailing '/' after the second-to-last element of keptPaths
    # in the for loop below, the trailing slash is preserved.
    numKept = len(keptPaths)
    if numKept > 0:
        for i in range(0, numKept-1):
            p = keptPaths[i]
            if len(p) > 0:
                #this will omit multiple slashes:
                path += p + b'/'
        path += keptPaths[numKept-1]

    return path

OCTAL_IP = re.compile(br"^(0[0-7]*)(\.[0-7]+)?(\.[0-7]+)?(\.[0-7]+)?$")
DECIMAL_IP = re.compile(br"^([1-9][0-9]*)(\.[0-9]+)?(\.[0-9]+)?(\.[0-9]+)?$")

def attemptIPFormats(host):
    if None == host:
        return None

    if host.isdigit():
        #mask hostname to lower four bytes to workaround issue with liveweb arc files
        return socket.inet_ntoa(
                struct.pack('>L', int(host) & 0xffffffff)).encode('ascii')
    else:
        m = DECIMAL_IP.match(host)
        if m:
            try:
                return socket.gethostbyname_ex(host)[2][0].encode('ascii')
            except (socket.gaierror, socket.herror):
                return None
        else:
            m = OCTAL_IP.match(host)
            if m:
                try:
                    return socket.gethostbyname_ex(host)[2][0].encode('ascii')
                except socket.gaierror:
                    return None

    return None

def minimalEscape(input):
    return escapeOnce(unescapeRepeatedly(input))

def escapeOnce(input):
    """escape everything outside of 32-128, except #"""
    if input:
        return quote_from_bytes(
                input, safe=b'''!"$&'()*+,-./:;<=>?@[\]^_`{|}~''').encode(
                        'ascii')
    else:
        return input


def unescapeRepeatedly(input):
    '''Argument may be str or bytes. Returns bytes.'''
    if None == input:
        return None

    while True:
        un = unquote_to_bytes(input)
        if un == input:
            return input
        input = un

_RES_PATH_SESSIONID = [
    re.compile(b"^(.*/)(\((?:[a-z]\([0-9a-z]{24}\))+\)/)([^\?]+\.aspx.*)$", re.I),
    re.compile(b"^(.*/)(\\([0-9a-z]{24}\\)/)([^\\?]+\\.aspx.*)$", re.I),
    ]

def stripPathSessionID(path):
    """It looks like the java version returns a lowercased path..
    So why does it uses a case-insensitive regex? We won't lowercase here.
    """
    for pattern in _RES_PATH_SESSIONID:
        m = pattern.match(path)
        if m:
            path = m.group(1) + m.group(3)

    return path


_RES_QUERY_SESSIONID = [
    re.compile(b"^(.*)(?:jsessionid=[0-9a-zA-Z]{32})(?:&(.*))?$", re.I),
    re.compile(b"^(.*)(?:phpsessid=[0-9a-zA-Z]{32})(?:&(.*))?$", re.I),
    re.compile(b"^(.*)(?:sid=[0-9a-zA-Z]{32})(?:&(.*))?$", re.I),
    re.compile(b"^(.*)(?:ASPSESSIONID[a-zA-Z]{8}=[a-zA-Z]{24})(?:&(.*))?$", re.I),
    re.compile(b"^(.*)(?:cfid=[^&]+&cftoken=[^&]+)(?:&(.*))?$", re.I),
    ]

def stripQuerySessionID(query):
    for pattern in _RES_QUERY_SESSIONID:
        m = pattern.match(query)
        if m:
            if m.group(2):
                query = m.group(1) + m.group(2)
            else:
                query = m.group(1)

    return query

def alphaReorderQuery(orig):
    # We cannot use urlparse.parse_qsl() here because it drops query arguments
    # without value (i.e. parse_qsl('foo=1&bar=&baz') returns [('foo', '1')]).
    # We want to keep them as Java version does.
    if orig is None or len(orig) <= 1:
        return orig

    args = orig.split(b'&')
    qas = [tuple(arg.split(b'=', 1)) for arg in args]
    qas.sort()

    return b'&'.join(
        t[0] if len(t) == 1 else t[0] + b'=' + t[1]
        for t in qas
        )

_RE_WWWDIGITS = re.compile(b'www\d*\.')

def massageHost(host):
    m = _RE_WWWDIGITS.match(host)
    if m:
        return host[len(m.group(0)):]
    else:
        return host

def getDefaultPort(scheme):
    scheme_lower = scheme.lower()
    if b'http' == scheme_lower:
        return 80
    elif b'https' == scheme_lower:
        return 443
    else:
        return 0

class GoogleURLCanonicalizer(object):
    """canonicalizer based on Google Safe Browser API usage guide.

    Reference: https://developers.google.com/safe-browsing/v4/urls-hashing
    """
    @staticmethod
    def canonicalize(url, **_ignored):
        """
        :parm url: parsed URL
        :type url: :class:`handyurl`
        """
        url.hash = None
        if url.authUser:
            url.authUser = minimalEscape(url.authUser)
        if url.authPass:
            url.authPass = minimalEscape(url.authPass)
        if url.query:
            url.query = minimalEscape(url.query)

        if url.host:
            host = unescapeRepeatedly(url.host)
            try:
                host.decode('ascii')
            except UnicodeDecodeError:
                try:
                    host = host.decode('utf-8', 'ignore').encode('idna')
                except ValueError:
                    pass

            host = host.replace(b'..', b'.').strip(b'.')

            ip = attemptIPFormats(host)
            if ip:
                host = ip;
            else:
                host = escapeOnce(host.lower())

            url.host = host

        path = unescapeRepeatedly(url.path)
        if url.host:
            path = normalizePath(path)
        # else path is free-form sort of thing, not /directory/thing
        url.path = escapeOnce(path)

        return url

class IAURLCanonicalizer(object):
    def __init__(self, host_lowercase=True, host_massage=True,
                 auth_strip_user=True, auth_strip_pass=True,
                 port_strip_default=True, path_strip_empty=False,
                 path_lowercase=True, path_strip_session_id=True,
                 path_strip_trailing_slash_unless_empty=True,
                 query_lowercase=True, query_strip_session_id=True,
                 query_strip_empty=True, query_alpha_reorder=True,
                 hash_strip=True, **_ignored):
        c = []
        if host_lowercase:
            c.append(self._host_lowercase)
        if host_massage:
            c.append(self._host_massage)
        if auth_strip_user:
            c.append(self._auth_strip_user)
        elif auth_strip_pass:
            c.append(self._auth_strip_pass)
        if port_strip_default:
            c.append(self._port_strip_default)
        if path_lowercase:
            c.append(self._path_lowercase)
        if path_strip_session_id:
            c.append(self._path_strip_session_id)
        if path_strip_empty:
            c.append(self._path_strip_empty)
        if path_strip_trailing_slash_unless_empty:
            c.append(self._path_strip_trailing_slash_unless_empty)
        if query_strip_session_id:
            c.append(self._query_strip_session_id)
        if query_lowercase:
            c.append(self._query_lowercase)
        if query_alpha_reorder:
            c.append(self._query_alpha_reorder)
        if query_strip_empty:
            c.append(self._query_strip_empty)

        self.canonicalizers = c

    # TODO: these function do not need to be instance methods. move them
    # to global scope?
    def _host_lowercase(self, hurl):
        if hurl.host:
            hurl.host = hurl.host.lower()
    def _host_massage(self, hurl):
        # java version calls massageHost regardless of scheme
        if hurl.host and hurl.scheme != b'dns':
            hurl.host = massageHost(hurl.host)
    def _auth_strip_user(self, hurl):
        hurl.authUser = None
        hurl.authPass = None
    def _auth_strip_pass(self, hurl):
        hurl.authPath = None
    def _port_strip_default(self, hurl):
        if hurl.scheme:
            defaultPort = getDefaultPort(hurl.scheme)
            if hurl.port == defaultPort:
                hurl.port = handyurl.DEFAULT_PORT
    def _path_lowercase(self, hurl):
        if hurl.path:
            hurl.path = hurl.path.lower()
    def _path_strip_session_id(self, hurl):
        if hurl.path:
            hurl.path = stripPathSessionID(hurl.path)
    def _path_strip_empty(self, hurl):
        if hurl.path == b'/':
            hurl.path = None
    def _path_strip_trailing_slash_unless_empty(self, hurl):
        path = hurl.path
        if path and len(path) > 1 and path.endswith(b'/'):
            hurl.path = hurl.path[:-1]
    def _query_strip_session_id(self, hurl):
        if hurl.query:
            hurl.query = stripQuerySessionID(hurl.query)
    def _query_lowercase(self, hurl):
        if hurl.query:
            hurl.query = hurl.query.lower()
    def _query_alpha_reorder(self, hurl):
        if hurl.query:
            hurl.query = alphaReorderQuery(hurl.query)
    def _query_strip_empty(self, hurl):
        # XXX setting last_delimiter=None only when hurl.qury is None
        # in the first place? this is what the code before refactoring
        # did, but probably we want to set None for hurl.query == b''
        # case as well?
        if hurl.query is None:
            hurl.last_delimiter = None
        elif hurl.query == b'':
            hurl.query = None

    def __call__(self, hurl):
        for c in self.canonicalizers:
            c(hurl)
        return hurl

    @classmethod
    def canonicalize(clazz, url, **options):
        """
        :parm url: parsed URL
        :type url: :class:`handyurl`
        """
        canonicalizer = clazz(**options)
        canonicalizer(url)
        return url

class DefaultIAURLCanonicalizer(object):
    @staticmethod
    def canonicalize(url, **options):
        """
        :parm url: parsed URL
        :type url: :class:`handyurl`
        """

        url = GoogleURLCanonicalizer.canonicalize(url, **options)
        url = IAURLCanonicalizer.canonicalize(url, **options)

        return url
