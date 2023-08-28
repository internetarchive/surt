#!/usr/bin/env python

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

"""This is a python port of IAURLCanonicalizer.java:
http://archive-access.svn.sourceforge.net/viewvc/archive-access/trunk/archive-access/projects/archive-commons/src/main/java/org/archive/url/IAURLCanonicalizer.java?view=markup
"""

from __future__ import absolute_import

import re

from surt.handyurl import handyurl
from surt.URLRegexTransformer import stripPathSessionID, stripQuerySessionID

# canonicalize()
#_______________________________________________________________________________
def canonicalize(url, host_lowercase=True, host_massage=True,
                 auth_strip_user=True, auth_strip_pass=True,
                 port_strip_default=True, path_strip_empty=False,
                 path_lowercase=True, path_strip_session_id=True,
                 path_strip_trailing_slash_unless_empty=True,
                 query_lowercase=True, query_strip_session_id=True,
                 query_strip_empty=True, query_alpha_reorder=True,
                 hash_strip=True, **_ignored):
    """The input url is a handyurl instance"""
    if host_lowercase and url.host:
        url.host = url.host.lower()

    if host_massage and url.host and (url.scheme != b'dns'): ###java version calls massageHost regardless of scheme
        url.host = massageHost(url.host)

    if auth_strip_user:
        url.authUser = None
        url.authPass = None
    elif auth_strip_pass:
        url.arthPass = None

    if port_strip_default and url.scheme:
        defaultPort = getDefaultPort(url.scheme)
        if url.port == defaultPort:
            url.port = handyurl.DEFAULT_PORT

    path = url.path
    if path_strip_empty and b'/' == path:
        url.path = None
    else:
        if path_lowercase and path:
            path = path.lower()
        if path_strip_session_id and path:
            path = stripPathSessionID(path)
        if path_strip_empty and b'/' == path:
            path = None
        if path_strip_trailing_slash_unless_empty and path:
            if path.endswith(b'/') and len(path)>1:
                path = path[:-1]

        url.path = path

    query = url.query
    if query:
        if len(query) > 0:
            if query_strip_session_id:
                query = stripQuerySessionID(query)
            if query_lowercase:
                query = query.lower()
            if query_alpha_reorder:
                query = alphaReorderQuery(query)
        if b'' == query and query_strip_empty:
            query = None
        url.query = query
    else:
        if query_strip_empty:
            url.last_delimiter = None

    return url


# alphaReorderQuery()
#_______________________________________________________________________________
def alphaReorderQuery(orig):
    """It's a shame that we can't use urlparse.parse_qsl() for this, but this
    function does keeps the trailing '=' if there is a query arg with no value:
    "?foo" vs "?foo=", and we want to exactly match the java version
    """


    if None == orig:
        return None

    if len(orig) <= 1:
        return orig

    args = orig.split(b'&')
    qas = [tuple(arg.split(b'=', 1)) for arg in args]
    qas.sort()

    s = b''
    for t in qas:
        if 1 == len(t):
            s += t[0] + b'&'
        else:
            s += t[0] + b'=' + t[1] + b'&'

    return s[:-1] #remove last &


# massageHost()
#_______________________________________________________________________________
_RE_WWWDIGITS = re.compile(rb'(www\d*\.).+\.')

def massageHost(host):
    m = _RE_WWWDIGITS.match(host)
    if m:
        return host[len(m.group(1)):]
    else:
        return host

# getDefaultPort()
#_______________________________________________________________________________
def getDefaultPort(scheme):
    scheme_lower = scheme.lower()
    if b'http' == scheme_lower:
        return 80
    elif b'https' == scheme_lower:
        return 443
    else:
        return 0

