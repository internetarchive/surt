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

"""This is a python port of the WaybackURLKeyMaker.java class:

http://archive-access.svn.sourceforge.net/viewvc/archive-access/trunk/archive-access/projects/archive-commons/src/main/java/org/archive/url/WaybackURLKeyMaker.java?view=markup
"""

from handyurl import handyurl
from URLRegexTransformer import hostToSURT
from DefaultIAURLCanonicalizer import canonicalize

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

    >>> surt("http://www.archive.org/")
    'org,archive)/'
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

    PHP session id:
    >>> surt("http://archive.org/index.php?PHPSESSID=0123456789abcdefghijklemopqrstuv&action=profile;u=4221")
    'org,archive)/index.php?action=profile;u=4221'

    WHOIS url:
    >>> surt("whois://whois.isoc.org.il/shaveh.co.il")
    'whois://whois.isoc.org.il/shaveh.co.il'

    Yahoo web bug. See https://github.com/internetarchive/surt/issues/1
    >>> surt('http://visit.webhosting.yahoo.com/visit.gif?&r=http%3A//web.archive.org/web/20090517140029/http%3A//anthonystewarthead.electric-chi.com/&b=Netscape%205.0%20%28Windows%3B%20en-US%29&s=1366x768&o=Win32&c=24&j=true&v=1.2')
    'com,yahoo,webhosting,visit)/visit.gif?&b=netscape%205.0%20(windows;%20en-us)&c=24&j=true&o=win32&r=http://web.archive.org/web/20090517140029/http://anthonystewarthead.electric-chi.com/&s=1366x768&v=1.2'
    """

    if not url:
        return "-"

    if url.startswith("filedesc"):
        return url

    if url.startswith("warcinfo"):
        return url

    if url.startswith("dns:"):
        return hostToSURT(url[4:]) + ')'

    if url.startswith("whois://"):
        return url

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
