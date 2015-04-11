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

from __future__ import absolute_import

from surt.handyurl import handyurl
from surt.URLRegexTransformer import hostToSURT

import surt.DefaultIAURLCanonicalizer as DefaultIAURLCanonicalizer

class CompositeCanonicalizer(object):
    def __init__(self, canonicalizers):
        self.caonicalizers = [
            self._normalize(canon) for canon in canonicalizers
            ]
    def __call__(self, hurl, **options):
        for canon in self.canonicalizers:
            hurl = canon(hurl, **options)
        return hurl
    @staticmethod
    def _normalize(canonicalizer):
        if hasattr(canonicalizer, '__call__'):
            return canonicalizer
        if hasattr(canonicalizer, 'canonicalize'):
            return canonicalizer.canonicalize
        raise AttributeError('canonicalizer must either is callable or have'
                             ' "canonicalizer" method')

# surt()
#_______________________________________________________________________________
def surt(url, canonicalizer=None, **options):
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

    # trailing comma mode
    >>> surt("http://archive.org/goo/?a=2&b&a=1", trailing_comma=True)
    'org,archive,)/goo?a=1&a=2&b'

    >>> surt("dns:archive.org", trailing_comma=True)
    'org,archive,)'

    >>> surt("warcinfo:foo.warc.gz", trailing_comma=True)
    'warcinfo:foo.warc.gz'

    PHP session id:
    >>> surt("http://archive.org/index.php?PHPSESSID=0123456789abcdefghijklemopqrstuv&action=profile;u=4221")
    'org,archive)/index.php?action=profile;u=4221'

    WHOIS url:
    >>> surt("whois://whois.isoc.org.il/shaveh.co.il")
    'whois://whois.isoc.org.il/shaveh.co.il'

    Yahoo web bug. See https://github.com/internetarchive/surt/issues/1
    >>> surt('http://visit.webhosting.yahoo.com/visit.gif?&r=http%3A//web.archive.org/web/20090517140029/http%3A//anthonystewarthead.electric-chi.com/&b=Netscape%205.0%20%28Windows%3B%20en-US%29&s=1366x768&o=Win32&c=24&j=true&v=1.2')
    'com,yahoo,webhosting,visit)/visit.gif?&b=netscape%205.0%20(windows;%20en-us)&c=24&j=true&o=win32&r=http://web.archive.org/web/20090517140029/http://anthonystewarthead.electric-chi.com/&s=1366x768&v=1.2'

    Simple customization:
    >>> surt("http://www.example.com/", canonicalizer=lambda x, **opts: x)
    'com,example,www)/'
    """

    if not url:
        return "-"

    if url.startswith("filedesc"):
        return url

    if url.startswith("warcinfo"):
        return url

    if url.startswith("dns:"):
        res = hostToSURT(url[4:])
        if options.get('trailing_comma'):
            res += ','
        res += ')'
        return res

    if url.startswith("whois://"):
        return url

    if canonicalizer is None:
        canonicalizer = DefaultIAURLCanonicalizer.canonicalize
    else:
        if isinstance(canonicalizer, (list, tuple)):
            canonicalizer = CompositeCanonicalizer(canonicalizer)
        elif (not hasattr(canonicalizer, '__call__') and
              hasattr(canonicalizer, 'canonicalize')):
            canonicalizer = canonicalizer.canonicalize

    if 'surt' not in options:
        options['surt'] = True

    hurl = canonicalizer(handyurl.parse(url), **options)
    key  = hurl.getURLString(**options)

    parenIdx = key.find('(')
    if -1 == parenIdx:
        return url #something very wrong

    return key[parenIdx+1:]


# main()
#_______________________________________________________________________________
if __name__ == "__main__":
    import doctest
    doctest.testmod()
