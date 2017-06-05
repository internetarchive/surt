#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from __future__ import absolute_import

import re
import tldextract
import collections

try:
    from urllib.parse import SplitResultBytes
except:
    from urlparse import SplitResult as SplitResultBytes

from surt.URLRegexTransformer import hostToSURT

_RE_MULTIPLE_PROTOCOLS = re.compile(br'^(https?://)+')
_RE_HAS_PROTOCOL = re.compile(b"^([a-zA-Z][a-zA-Z0-9\+\-\.]*):")
_RE_SPACES = re.compile(b'[\n\r\t]')

class handyurl(object):
    """A python port of the archive-commons org.archive.url HandyURL class

    To simplify the surt module, we add the URLParser.parse method here,
    which makes the URLParser class unnecessary. handyurl becomes a thin
    wrapper around python's urlparse module.

    Init an empty class:
    >>> h = handyurl()

    Init with just a host:
    >>> h = handyurl(host='www.amazon.co.uk')

    This version of handyurl contains a field for last_delimiter, to allow
    a url to roundtrip through this class without modification. From the
    urlparse docs:
    "This [roundtripping] may result in a slightly different, but equivalent URL,
    if the URL that was parsed originally had unnecessary delimiters
    (for example, a ? with an empty query; the RFC states that these are equivalent)."
    We want the url http://www.google.com/? to work, since there is a test for
    it in the GoogleURLCanonicalizer class. Note, however, the IAURLCanonicalizer
    class strips empty queries.
    """
    DEFAULT_PORT = None

    # init
    #___________________________________________________________________________
    def __init__(self, scheme=None, authUser=None, authPass=None,
                 host=None, port=DEFAULT_PORT, path=None,
                 query=None, hash=None, last_delimiter=None):
        self.scheme   = scheme
        self.authUser = authUser
        self.authPass = authPass
        self.host     = host
        self.port     = port
        self.path     = path
        self.query    = query
        self.hash     = hash
        self.last_delimiter = last_delimiter #added in python version


    '''
    RFC 2396-inspired regex.

    From the RFC Appendix B:
    <pre>
    URI Generic Syntax                August 1998

    B. Parsing a URI Reference with a Regular Expression

    As described in Section 4.3, the generic URI syntax is not sufficient
    to disambiguate the components of some forms of URI.  Since the
    "greedy algorithm" described in that section is identical to the
    disambiguation method used by POSIX regular expressions, it is
    natural and commonplace to use a regular expression for parsing the
    potential four components and fragment identifier of a URI reference.

    The following line is the regular expression for breaking-down a URI
    reference into its components.

    ^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?
     12            3  4          5       6  7        8 9

    The numbers in the second line above are only to assist readability;
    they indicate the reference points for each subexpression (i.e., each
    paired parenthesis).  We refer to the value matched for subexpression
    <n> as $<n>.  For example, matching the above expression to

    http://www.ics.uci.edu/pub/ietf/uri/#Related

    results in the following subexpression matches:

    $1 = http:
    $2 = http
    $3 = //www.ics.uci.edu
    $4 = www.ics.uci.edu
    $5 = /pub/ietf/uri/
    $6 = <undefined>
    $7 = <undefined>
    $8 = #Related
    $9 = Related

    where <undefined> indicates that the component is not present, as is
    the case for the query component in the above example.  Therefore, we
    can determine the value of the four components and fragment as

    scheme    = $2
    authority = $4
    path      = $5
    query     = $7
    fragment  = $9
    </pre>

    --
    Below differs from the rfc regex in that...
    (1) we allow a URI made of a fragment only (Added extra
    group so indexing is off by one after scheme).
    (2) scheme is limited to legal scheme characters

    1: scheme:
    2: scheme
    3: //authority/path
    4: //authority
    5: authority (aka netloc)
    6: path
    7: ?query
    8: query
    9: #fragment
    A: fragment
    '''
    RFC2396REGEX = re.compile(br'^(([a-zA-Z][a-zA-Z0-9+.-]*):)?((//([^/?#]*))?([^?#]*)(\?([^#]*))?)?(#(.*))?$')
    # group open:                 12                           34  5          6       7  8          9 A
    # group close:                                         2 1             54        6         87 3      A9

    @classmethod
    def urlsplit(cls, url):
        """Similar to urllib.parse.urlsplit, but does not try to decode raw
        bytes. (Library method fails on non-ascii)"""
        assert isinstance(url, bytes)

        m = cls.RFC2396REGEX.match(url)
        assert m

        return SplitResultBytes(m.group(2) or b'', m.group(5) or b'',
                                m.group(6) or b'', m.group(8) or b'',
                                m.group(10) or b'')

    # parse() classmethod
    #___________________________________________________________________________
    @classmethod
    def parse(cls, url):
        u"""This method was in the java URLParser class, but we don't need
        a whole class to parse a url, when we can just use python's urlparse.

        """

        if not isinstance(url, bytes):
            url = url.encode('utf-8')

        # Note RE_SPACES does not match regular space (0x20). That is,
        # regular spaces are removed at head and tail, but not in the middle.
        # There's a test case for GoogleURLCanonicalizer.canonicalize that
        # asserts this behavior.
        url = url.strip()
        url = _RE_SPACES.sub(b'', url)

        url = cls.addDefaultSchemeIfNeeded(url)

        #From Tymm: deal with http://https/order.1and1.com
        url = _RE_MULTIPLE_PROTOCOLS.sub(lambda m: m.group(1), url)

        o = cls.urlsplit(url)

        scheme   = o.scheme   or None
        query    = o.query    or None
        fragment = o.fragment or None

        """Deal with hostnames that end with ':' without being followed by a port number"""
        if o.netloc.endswith(b':'):
            o = o._replace(netloc=o.netloc.rstrip(b':'))
        port     = o.port     or None

        hostname = o.hostname or None
        path     = o.path     or None

        if scheme.startswith(b'http'):
            #deal with "http:////////////////www.vikings.com"
            if hostname is None and path is not None:
                parts    = path.lstrip(b'/').partition(b'/')
                hostname = parts[0]
                path     = b'/'+parts[2]

        h = cls(scheme = scheme,
                host   = hostname,
                path   = path,
                query  = query,
                hash   = fragment,
                port   = port,
               )

        #See note at top about last_delimiter
        if url.endswith(b'?') and None == h.query:
            h.last_delimiter = b'?'

        return h

    # addDefaultSchemeIfNeeded()
    #___________________________________________________________________________
    """copied from URLParser.java"""
    @classmethod
    def addDefaultSchemeIfNeeded(cls, url):
        if not url:
            return url

        ###noah: accept anything that looks like it starts with a scheme:
        if _RE_HAS_PROTOCOL.match(url):
            return url
        else:
            return b"http://"+url

    # geturl()
    #___________________________________________________________________________
    def geturl(self):
        """urlparse.ParseResult has a geturl() method, so we have one too.
        Nicer than typing the java method name!
        """
        return self.getURLString()

    # getURLString()
    #___________________________________________________________________________
    def getURLString(self, **options):
        return self.geturl_bytes(**options).decode('utf-8')

    def geturl_bytes(self,
                     surt=False,
                     public_suffix=False,
                     trailing_comma=False,
                     reverse_ipaddr=True,
                     with_scheme=True,
                     **options):
        hostSrc = self.host
        if hostSrc:
            if public_suffix:
                hostSrc = self.getPublicSuffix()
            if surt:
                hostSrc = hostToSURT(hostSrc, reverse_ipaddr)

        if with_scheme:
            s = self.scheme + b':'
            if hostSrc:
                if self.scheme != b'dns':
                    s += b'//'
                if surt:
                    s += b"("
        elif not hostSrc:
            s = self.scheme + b':'
        else:
            s = b''

        if hostSrc:
            if self.authUser:
                s += self.authUser
                if self.authPass:
                    s += self.authPass
                s += b'@'

            s += hostSrc

            if self.port != self.DEFAULT_PORT:
                s += (":%d" % self.port).encode('utf-8')

            if surt:
                if trailing_comma:
                    s += b','
                s += b')'

        if self.path:
            s += self.path
        elif self.query is not None or self.hash is not None:
            #must have '/' with query or hash:
            s += b'/'

        if None != self.query:
            s += b'?' + self.query
        if None != self.hash:
            s += b'#' + self.hash

        if None != self.last_delimiter:
            s += self.last_delimiter

        return s

    # getPublicSuffix
    #___________________________________________________________________________
    def getPublicSuffix(self):
        """Uses the tldextract module to get the public suffix via the
        Public Suffix List.
        """
        return tldextract.extract(self.host).registered_domain.encode('ascii')

    # getPublicPrefix
    #___________________________________________________________________________
    def getPublicPrefix(self):
        """Uses the tldextract module to get the subdomain, using the
        Public Suffix List.
        """
        return tldextract.extract(self.host).subdomain

    # repr
    #___________________________________________________________________________
    # commented out because of http://bugs.python.org/issue5876
    # "__repr__ returning unicode doesn't work when called implicitly"
    #def __repr__(self):
    #    return u"""handyurl(scheme=%s, authUser=%s, authPass=%s, host=%s, port=%s, path=%s, query=%s, hash=%s)""".encode('utf-8') % (self.scheme, self.authUser, self.authPass, self.host, self.port, self.path, self.query, self.hash)
