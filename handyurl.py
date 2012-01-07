#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tldextract
from urlparse import urlparse
from URLRegexTransformer import hostToSURT

class handyurl(object):
    """A python port of the archive-commons org.archive.url HandyURL class

    To simplify the surt module, we add the URLParser.parse method here,
    which makes the URLParser class unnecessary. handyurl becomes a thin
    wrapper around python's urlparse module.

    Init an empty class:
    >>> h = handyurl()

    Init with just a host:
    >>> h = handyurl(host='www.amazon.co.uk')
    """
    DEFAULT_PORT = None

    # init
    #___________________________________________________________________________
    def __init__(self, scheme=None, authUser=None, authPass=None,
                 host=None, port=DEFAULT_PORT, path=None,
                 query=None, hash=None, opaque=None):
        self.scheme   = scheme
        self.authUser = authUser
        self.authPass = authPass
        self.host     = host
        self.port     = port
        self.path     = path
        self.query    = query
        self.hash     = hash
        self.opaque   = opaque

    # parse() classmethod
    #___________________________________________________________________________
    @classmethod
    def parse(cls, url):
        """This method was in the java URLParser class, but we don't need
        a whole class to parse a url, when we can just use python's urlparse.

        These doctests come from URLParserTest.java:

        >>> handyurl.parse("http://www.archive.org/index.html#foo")
        handyurl(scheme=http, authUser=None, authPass=None, host=www.archive.org, port=None, path=/index.html, query=None, hash=foo, opaque=None)

        >>> handyurl.parse("http://www.archive.org/")
        handyurl(scheme=http, authUser=None, authPass=None, host=www.archive.org, port=None, path=/, query=None, hash=None, opaque=None)

        >>> handyurl.parse("http://www.archive.org")
        handyurl(scheme=http, authUser=None, authPass=None, host=www.archive.org, port=None, path=None, query=None, hash=None, opaque=None)

        >>> handyurl.parse("http://www.archive.org?")
        handyurl(scheme=http, authUser=None, authPass=None, host=www.archive.org, port=None, path=None, query=None, hash=None, opaque=None)

        >>> handyurl.parse("http://www.archive.org:8080/index.html?query#foo")
        handyurl(scheme=http, authUser=None, authPass=None, host=www.archive.org, port=8080, path=/index.html, query=query, hash=foo, opaque=None)

        >>> handyurl.parse("http://www.archive.org:8080/index.html?#foo")
        handyurl(scheme=http, authUser=None, authPass=None, host=www.archive.org, port=8080, path=/index.html, query=None, hash=foo, opaque=None)

        >>> handyurl.parse("http://www.archive.org:8080?#foo")
        handyurl(scheme=http, authUser=None, authPass=None, host=www.archive.org, port=8080, path=None, query=None, hash=foo, opaque=None)

        >>> handyurl.parse("http://bücher.ch:8080?#foo")
        handyurl(scheme=http, authUser=None, authPass=None, host=bücher.ch, port=8080, path=None, query=None, hash=foo, opaque=None)

        >>> handyurl.parse("dns:bücher.ch")
        handyurl(scheme=dns, authUser=None, authPass=None, host=bücher.ch, port=None, path=None, query=None, hash=None, opaque=None)
        """

        o = urlparse(url)

        scheme   = o.scheme   or None
        query    = o.query    or None
        fragment = o.fragment or None
        port     = o.port     or None

        if 'dns' == scheme:
            hostname = o.path or None
            path     = None
        else:
            hostname = o.hostname or None
            path     = o.path     or None

        h = cls(scheme = scheme,
                host   = hostname,
                path   = path,
                query  = query,
                hash   = fragment,
                port   = port,
               )
        return h

    # getURLString()
    #___________________________________________________________________________
    def getURLString(self, surt=False, public_suffix=False):
        """Don't use this on dns urls"""

        if None != self.opaque:
			return self.opaque #wonder what this is for...

        if 'dns' == self.scheme:
            s = self.scheme + ':'   ###java version adds :// regardless of scheme
        else:
            s = self.scheme + '://'
        if surt:
            s += "("

        if self.authUser:
            s += self.authUser
            if self.authPass:
                s += self.authPass
            s += '@'

        hostSrc = self.host
        if public_suffix:
            hostSrc = self.getPublicSuffix()
        if surt:
            hostSrc = hostToSURT(hostSrc)
        s += hostSrc

        if self.port != self.DEFAULT_PORT:
            s += ":%d" % self.port

        if surt:
            s += ')'

        hasPath = (None != self.path) and (len(self.path) > 0)
        if hasPath:
            s += self.path
        else:
            if (None != self.query) or (None != self.hash):
                #must have '/' with query or hash:
                s += '/'

        if None != self.query:
            s += '?' + self.query
        if None != self.hash:
            s += '#' + self.hash

        return s

    # getPublicSuffix
    #___________________________________________________________________________
    def getPublicSuffix(self):
        """Uses the tldextract module to get the public suffix via the
        Public Suffix List.

        These doctests are based off the ones found in HandyURLTest.java:

        >>> h = handyurl(host='www.fool.com')
        >>> h.getPublicSuffix()
        'fool.com'

        >>> h = handyurl(host='www.amazon.co.uk')
        >>> h.getPublicSuffix()
        'amazon.co.uk'

        >>> h = handyurl(host='www.images.amazon.co.uk')
        >>> h.getPublicSuffix()
        'amazon.co.uk'

        >>> h = handyurl(host='funky-images.fancy.co.jp')
        >>> h.getPublicSuffix()
        'fancy.co.jp'
        """

        r = tldextract.extract(self.host)
        return "%s.%s" % (r.domain, r.tld)


    # getPublicPrefix
    #___________________________________________________________________________
    def getPublicSuffix(self):
        """Uses the tldextract module to get the subdomain, using the
        Public Suffix List.

        These doctests are based off the ones found in HandyURLTest.java:

        >>> h = handyurl(host='www.fool.com')
        >>> h.getPublicSuffix()
        'www'

        >>> h = handyurl(host='www.amazon.co.uk')
        >>> h.getPublicSuffix()
        'www'

        >>> h = handyurl(host='www.images.amazon.co.uk')
        >>> h.getPublicSuffix()
        'www.images'

        >>> h = handyurl(host='funky-images.fancy.co.jp')
        >>> h.getPublicSuffix()
        'funky-images'
        """
        return tldextract.extract(self.host).subdomain

    # repr
    #___________________________________________________________________________
    def __repr__(self):
        return """handyurl(scheme=%s, authUser=%s, authPass=%s, host=%s, port=%s, path=%s, query=%s, hash=%s, opaque=%s)""" % (self.scheme, self.authUser, self.authPass, self.host, self.port, self.path, self.query, self.hash, self.opaque)


# main()
#_______________________________________________________________________________
if __name__ == "__main__":
    import doctest
    doctest.testmod()
