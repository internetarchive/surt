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
