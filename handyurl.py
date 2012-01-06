#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tldextract
from urlparse import urlparse

class handyurl(object):
    """A python port of the archive-commons org.archive.url HandyURL class

    To simply the module, we add the URLParser.parse method as a classmethod,
    which makes the URLParser class unnecessary.

    Init an empty class:
    >>> h = handyurl()

    Init with just a host:
    >>> h = handyurl(host='www.amazon.co.uk')
    """
    DEFAULT_PORT = -1;

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
        handyurl(scheme=dns, authUser=None, authPass=None, host=None, port=None, path=bücher.ch, query=None, hash=None, opaque=None)
        """

        o = urlparse(url)

        scheme   = o.scheme   or None
        hostname = o.hostname or None
        path     = o.path     or None
        query    = o.query    or None
        fragment = o.fragment or None
        port     = o.port     or None

        h = cls(scheme = scheme,
                host   = hostname,
                path   = path,
                query  = query,
                hash   = fragment,
                port   = port,
               )
        return h

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
