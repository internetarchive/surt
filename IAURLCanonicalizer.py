#!/usr/bin/env python

"""This is a python port of IAURLCanonicalizer.java:
http://archive-access.svn.sourceforge.net/viewvc/archive-access/trunk/archive-access/projects/archive-commons/src/main/java/org/archive/url/IAURLCanonicalizer.java?view=markup

The doctests are copied from IAURLCanonicalizerTest.java:
http://archive-access.svn.sourceforge.net/viewvc/archive-access/trunk/archive-access/projects/archive-commons/src/test/java/org/archive/url/IAURLCanonicalizerTest.java?view=markup
"""

import re
from handyurl import handyurl
from URLRegexTransformer import stripPathSessionID, stripQuerySessionID

# canonicalize()
#_______________________________________________________________________________
def canonicalize(url, host_lowercase=True, host_massage=True,
                 auth_strip_user=True, auth_strip_pass=True,
                 port_strip_default=True, path_strip_empty=False,
                 path_lowercase=True, path_strip_session_id=True,
                 path_strip_trailing_slash_unless_empty=True,
                 query_lowercase=True, query_strip_session_id=True,
                 query_strip_empty=True, query_alpha_reorder=True,
                 hash_strip=True):
    """The input url is a handyurl instance

    These doctests are from IAURLCanonicalizerTest.java:

    >>> canonicalize(handyurl.parse("http://ARCHIVE.ORG/")).getURLString()
    'http://archive.org/'
    >>> canonicalize(handyurl.parse("http://www.archive.org:80/")).getURLString()
    'http://archive.org/'
    >>> canonicalize(handyurl.parse("https://www.archive.org:80/")).getURLString()
    'https://archive.org:80/'
    >>> canonicalize(handyurl.parse("http://www.archive.org:443/")).getURLString()
    'http://archive.org:443/'
    >>> canonicalize(handyurl.parse("https://www.archive.org:443/")).getURLString()
    'https://archive.org/'
    >>> canonicalize(handyurl.parse("http://www.archive.org/big/")).getURLString()
    'http://archive.org/big'
    >>> canonicalize(handyurl.parse("dns:www.archive.org")).getURLString()
    'dns:www.archive.org'
    """
    if host_lowercase and url.host:
        url.host = url.host.lower()

    if host_massage and url.host and (url.scheme != 'dns'): ###java version calls massageHost regardless of scheme
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
    if path_strip_empty and '/' == path:
        url.path = None
    else:
        if path_lowercase and path:
            path = path.lower()
        if path_strip_session_id and path:
            path = stripPathSessionID(path)
        if path_strip_empty and '/' == path:
            path = None
        if path_strip_trailing_slash_unless_empty and path:
            if path.endswith("/") and len(path)>1:
                path = path[:-1]

        url.path = path

    query = url.query
    if query:
        if '' == query and query_strip_empty:
            query = None
        elif len(query) > 0:
            if query_strip_session_id:
                #This function expects the query to start with a '?'
                query = stripQuerySessionID('?'+query)
                query = query[1:] #now strip off '?' that we just added
            if query_lowercase:
                query = query.lower()
            if query_alpha_reorder:
                query = alphaReorderQuery(query)
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

    These doctests are from IAURLCanonicalizerTest.java:

    >>> alphaReorderQuery(None)
    >>> alphaReorderQuery("")
    ''
    >>> alphaReorderQuery("")
    ''
    >>> alphaReorderQuery("a")
    'a'
    >>> alphaReorderQuery("ab")
    'ab'
    >>> alphaReorderQuery("a=1")
    'a=1'
    >>> alphaReorderQuery("ab=1")
    'ab=1'
    >>> alphaReorderQuery("a=1&")
    '&a=1'
    >>> alphaReorderQuery("a=1&b=1")
    'a=1&b=1'
    >>> alphaReorderQuery("b=1&a=1")
    'a=1&b=1'
    >>> alphaReorderQuery("a=a&a=a")
    'a=a&a=a'
    >>> alphaReorderQuery("a=b&a=a")
    'a=a&a=b'
    >>> alphaReorderQuery("b=b&a=b&b=a&a=a")
    'a=a&a=b&b=a&b=b'
    """


    if None == orig:
        return None

    if len(orig) <= 1:
        return orig

    args = orig.split("&")
    qas = [tuple(arg.split('=', 1)) for arg in args]
    qas.sort()

    s = ''
    for t in qas:
        if 1 == len(t):
            s += t[0] + '&'
        else:
            s += t[0] + '=' + t[1] + '&'

    return s[:-1] #remove last &


# massageHost()
#_______________________________________________________________________________
def massageHost(host):
    """These doctests are from IAURLCanonicalizerTest.java:

    >>> massageHost("foo.com")
    'foo.com'
    >>> massageHost("www.foo.com")
    'foo.com'
    >>> massageHost("www12.foo.com")
    'foo.com'

    >>> massageHost("www2foo.com")
    'www2foo.com'
    >>> massageHost("www2.www2foo.com")
    'www2foo.com'
    """

    m = re.match('www\d*\.', host)
    if m:
        return host[len(m.group(0)):]
    else:
        return host

# getDefaultPort()
#_______________________________________________________________________________
def getDefaultPort(scheme):
    """These doctests are from IAURLCanonicalizerTest.java:

    >>> getDefaultPort("foo")
    0
    >>> getDefaultPort("http")
    80
    >>> getDefaultPort("https")
    443
    """
    scheme_lower = scheme.lower()
    if 'http' == scheme_lower:
        return 80
    elif 'https' == scheme_lower:
        return 443
    else:
        return 0

# main()
#_______________________________________________________________________________
if __name__ == "__main__":
    import doctest
    doctest.testmod()

