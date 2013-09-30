#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import tldextract
from urlparse import urlsplit
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
                 query=None, hash=None, opaque=None, last_delimiter=None):
        self.scheme   = scheme
        self.authUser = authUser
        self.authPass = authPass
        self.host     = host
        self.port     = port
        self.path     = path
        self.query    = query
        self.hash     = hash
        self.opaque   = opaque
        self.last_delimiter = last_delimiter #added in python version

    # parse() classmethod
    #___________________________________________________________________________
    @classmethod
    def parse(cls, url):
        u"""This method was in the java URLParser class, but we don't need
        a whole class to parse a url, when we can just use python's urlparse.

        These doctests come from URLParserTest.java:

        >>> handyurl.parse("http://www.archive.org/index.html#foo").geturl()
        'http://www.archive.org/index.html#foo'

        >>> handyurl.parse("http://www.archive.org/").geturl()
        'http://www.archive.org/'

        >>> handyurl.parse("http://www.archive.org").geturl()
        'http://www.archive.org'

        >>> handyurl.parse("http://www.archive.org?").geturl()
        'http://www.archive.org?'

        >>> handyurl.parse("http://www.archive.org:8080/index.html?query#foo").geturl()
        'http://www.archive.org:8080/index.html?query#foo'

        >>> handyurl.parse("http://www.archive.org:8080/index.html?#foo").geturl()
        'http://www.archive.org:8080/index.html#foo'

        >>> handyurl.parse("http://www.archive.org:8080?#foo").geturl()
        'http://www.archive.org:8080/#foo'

        >>> print handyurl.parse(u"http://bücher.ch:8080?#foo").geturl()
        http://b\xfccher.ch:8080/#foo

        >>> print handyurl.parse(u"dns:bücher.ch").geturl()
        dns:b\xfccher.ch

        ###From Tymm:
        >>> handyurl.parse("http:////////////////www.vikings.com").geturl()
        'http://www.vikings.com/'
        >>> handyurl.parse("http://https://order.1and1.com").geturl()
        'https://order.1and1.com'

        ###From Common Crawl, host ends with ':' without a port number
        >>> handyurl.parse("http://mineral.galleries.com:/minerals/silicate/chabazit/chabazit.htm").geturl()
        'http://mineral.galleries.com/minerals/silicate/chabazit/chabazit.htm'
        """
        url = url.strip()
        url = re.sub('[\n\r\t]', '', url)

        ### DNS URLs are treated separately as opaque urls by URLParser.java
        # However, we want to surtify dns urls as well.
        if re.match("^(filedesc|warcinfo):.*", url):
            return cls(opaque=url)

        url = cls.addDefaultSchemeIfNeeded(url)

        #From Tymm: deal with http://https/order.1and1.com
        url = re.sub('^(https?://)+', r'\1', url)

        """The java code seems to use this regex:
        re.compile("^(([a-zA-Z][a-zA-Z0-9\+\-\.]*):)?((//([^/?#]*))?([^?#]*)(\?([^#]*))?)?(#(.*))?")
        """
        o = urlsplit(url)

        scheme   = o.scheme   or None
        query    = o.query    or None
        fragment = o.fragment or None

        """Deal with hostnames that end with ':' without being followed by a port number"""
        if o.netloc.endswith(':'):
            o = o._replace(netloc=o.netloc.rstrip(':'))
        port     = o.port     or None

        """One more special-case for dns urls or broken http urls. From the docs:
        Following the syntax specifications in RFC 1808, urlparse recognizes
        a netloc only if it is properly introduced by ‘//’. Otherwise the input
        is presumed to be a relative URL and thus to start with a path component.
        """
        if 'dns' == scheme:
            hostname = o.path or None
            path     = None
        else:
            hostname = o.hostname or None
            path     = o.path     or None

        if scheme.startswith('http'):
            #deal with "http:////////////////www.vikings.com"
            if hostname is None and path is not None:
                parts    = path.lstrip('/').partition('/')
                hostname = parts[0]
                path     = '/'+parts[2]

        h = cls(scheme = scheme,
                host   = hostname,
                path   = path,
                query  = query,
                hash   = fragment,
                port   = port,
               )

        #See note at top about last_delimiter
        if url.endswith('?') and None == h.query:
            h.last_delimiter = '?'

        return h

    # addDefaultSchemeIfNeeded()
    #___________________________________________________________________________
    """copied from URLParser.java"""
    @classmethod
    def addDefaultSchemeIfNeeded(cls, url):
        if not url:
            return url

        ###raj: DNS URLs are treated separately as opaque urls by URLParser.java,
        #but we want to surtify dns urls as well
        if url.startswith('dns:'):
            return url

        if re.match("^(http|https|ftp|mms|rtsp|wais)://.*", url):
            return url
        else:
            return "http://"+url

    # geturl()
    #___________________________________________________________________________
    def geturl(self):
        """urlparse.ParseResult has a geturl() method, so we have one too.
        Nicer than typing the java method name!
        """
        return self.getURLString()

    # getURLString()
    #___________________________________________________________________________
    def getURLString(self, surt=False, public_suffix=False):

        if None != self.opaque:
			return self.opaque

        if 'dns' == self.scheme:
            s = self.scheme + ':'   ###java version adds :// regardless of scheme
        else:                       ###java version uses opaque type for dns urls, but this version supports dns urls
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

        if None != self.last_delimiter:
            s += self.last_delimiter

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
    # commented out because of http://bugs.python.org/issue5876
    # "__repr__ returning unicode doesn't work when called implicitly"
    #def __repr__(self):
    #    return u"""handyurl(scheme=%s, authUser=%s, authPass=%s, host=%s, port=%s, path=%s, query=%s, hash=%s, opaque=%s)""".encode('utf-8') % (self.scheme, self.authUser, self.authPass, self.host, self.port, self.path, self.query, self.hash, self.opaque)



# main()
#_______________________________________________________________________________
if __name__ == "__main__":
    import doctest
    doctest.testmod()
