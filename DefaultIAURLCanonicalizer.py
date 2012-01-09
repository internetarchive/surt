#!/usr/bin/env python

"""This is a python port of DefaultIAURLCanonicalizer.java:
http://archive-access.svn.sourceforge.net/viewvc/archive-access/trunk/archive-access/projects/archive-commons/src/main/java/org/archive/url/DefaultIAURLCanonicalizer.java?view=markup

The doctests are copied from DefaultIAURLCanonicalizerTest.java:
http://archive-access.svn.sourceforge.net/viewvc/archive-access/trunk/archive-access/projects/archive-commons/src/test/java/org/archive/url/DefaultIAURLCanonicalizerTest.java?view=markup
"""

import GoogleURLCanonicalizer
import IAURLCanonicalizer

# canonicalize()
#_______________________________________________________________________________
def canonicalize(url):
    """The input url is a handyurl instance

    These doctests are from DefaultIAURLCanonicalizerTest.java:

    >>> from handyurl import handyurl
    >>> canonicalize(handyurl.parse("http://www.alexa.com/")).getURLString()
    'http://alexa.com/'
    >>> canonicalize(handyurl.parse("http://archive.org/index.html")).getURLString()
    'http://archive.org/index.html'
    >>> canonicalize(handyurl.parse("http://archive.org/index.html?")).getURLString()
    'http://archive.org/index.html'
    >>> canonicalize(handyurl.parse("http://archive.org/index.html?a=b")).getURLString()
    'http://archive.org/index.html?a=b'
    >>> canonicalize(handyurl.parse("http://archive.org/index.html?b=b&a=b")).getURLString()
    'http://archive.org/index.html?a=b&b=b'
    >>> canonicalize(handyurl.parse("http://archive.org/index.html?b=a&b=b&a=b")).getURLString()
    'http://archive.org/index.html?a=b&b=a&b=b'
    >>> canonicalize(handyurl.parse("http://www34.archive.org/index.html?b=a&b=b&a=b")).getURLString()
    'http://archive.org/index.html?a=b&b=a&b=b'
    """

    url = GoogleURLCanonicalizer.canonicalize(url)
    url = IAURLCanonicalizer.canonicalize(url)

    return url

# main()
#_______________________________________________________________________________
if __name__ == "__main__":
    import doctest
    doctest.testmod()
