#!/usr/bin/env python

import tldextract

class handyurl(object):
    """A python port of the archive-commons org.archive.url HandyURL class

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


# main()
#_______________________________________________________________________________
if __name__ == "__main__":
    import doctest
    doctest.testmod()
