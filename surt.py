#!/usr/bin/env python

"""This is a python port of the WaybackURLKeyMaker.java class:

http://archive-access.svn.sourceforge.net/viewvc/archive-access/trunk/archive-access/projects/archive-commons/src/main/java/org/archive/url/WaybackURLKeyMaker.java?view=markup
"""

from handyurl import handyurl
from URLRegexTransformer import hostToSURT
from IAURLCanonicalizer import canonicalize
#NOTE: the java version using a different canonicalizer!

# surt()
#_______________________________________________________________________________
def surt(url):
    """
    These doctests are from WaybackURLKeyMakerTest.java

    >>> surt(None)
    '-'
    >>> surt('')
    '-'
    >>> surt("filedesc:foo.arc.gz")
    'filedesc:foo.arc.gz'
    >>> surt("filedesc:/foo.arc.gz")
    'filedesc:/foo.arc.gz'
    >>> surt("filedesc://foo.arc.gz")
    'filedesc://foo.arc.gz'
    >>> surt("warcinfo:foo.warc.gz")
    'warcinfo:foo.warc.gz'
    >>> surt("dns:alexa.com")
    'com,alexa)'
    >>> surt("dns:archive.org")
    'org,archive)'

    >>> surt("http://archive.org/")
    'org,archive)/'
    >>> surt("http://archive.org/goo/")
    'org,archive)/goo'
    >>> surt("http://archive.org/goo/?")
    'org,archive)/goo'
    >>> surt("http://archive.org/goo/?b&a")
    'org,archive)/goo?a&b'
    >>> surt("http://archive.org/goo/?a=2&b&a=1")
    'org,archive)/goo?a=1&a=2&b'
    """

    if not url:
        return "-"

    if url.startswith("filedesc"):
        return url

    if url.startswith("warcinfo"):
        return url

    if url.startswith("dns:"):
        return hostToSURT(url[4:]) + ')'

    hurl = canonicalize(handyurl.parse(url))
    key  = hurl.getURLString(surt=True)

    parenIdx = key.find('(')
    if -1 == parenIdx:
        return url #something very wrong

    return key[parenIdx+1:]


# main()
#_______________________________________________________________________________
if __name__ == "__main__":
    import doctest
    doctest.testmod()
