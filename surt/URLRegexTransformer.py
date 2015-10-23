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

"""This is a python port of URLRegexTransformer.java:
http://archive-access.svn.sourceforge.net/viewvc/archive-access/trunk/archive-access/projects/archive-commons/src/main/java/org/archive/url/URLRegexTransformer.java?view=markup

The doctests are copied from URLRegexTransformerTest.java:
http://archive-access.svn.sourceforge.net/viewvc/archive-access/trunk/archive-access/projects/archive-commons/src/test/java/org/archive/url/URLRegexTransformerTest.java?view=markup
"""

import re

# stripPathSessionID
#_______________________________________________________________________________
_RES_PATH_SESSIONID = [
    re.compile("^(.*/)(\((?:[a-z]\([0-9a-z]{24}\))+\)/)([^\?]+\.aspx.*)$", re.I),
    re.compile("^(.*/)(\\([0-9a-z]{24}\\)/)([^\\?]+\\.aspx.*)$", re.I),
    ]

def stripPathSessionID(path):
    """It looks like the java version returns a lowercased path..
    So why does it uses a case-insensitive regex? We won't lowercase here.

    These doctests are from IAURLCanonicalizerTest.java:

	Check ASP_SESSIONID2:
	>>> stripPathSessionID("/(S(4hqa0555fwsecu455xqckv45))/mileg.aspx")
	'/mileg.aspx'

    Check ASP_SESSIONID2 (again):
    >>> stripPathSessionID("/(4hqa0555fwsecu455xqckv45)/mileg.aspx")
    '/mileg.aspx'

    Check ASP_SESSIONID3:
    >>> stripPathSessionID("/(a(4hqa0555fwsecu455xqckv45)S(4hqa0555fwsecu455xqckv45)f(4hqa0555fwsecu455xqckv45))/mileg.aspx?page=sessionschedules")
    '/mileg.aspx?page=sessionschedules'

    '@' in path:
    >>> stripPathSessionID("/photos/36050182@N05/")
    '/photos/36050182@N05/'
    """
    for pattern in _RES_PATH_SESSIONID:
        m = pattern.match(path)
        if m:
            path = m.group(1) + m.group(3)

    return path


# stripQuerySessionID
#_______________________________________________________________________________
_RES_QUERY_SESSIONID = [
    re.compile("^(.+)(?:jsessionid=[0-9a-zA-Z]{32})(?:&(.*))?$", re.I),
    re.compile("^(.+)(?:phpsessid=[0-9a-zA-Z]{32})(?:&(.*))?$", re.I),
    re.compile("^(.+)(?:sid=[0-9a-zA-Z]{32})(?:&(.*))?$", re.I),
    re.compile("^(.+)(?:ASPSESSIONID[a-zA-Z]{8}=[a-zA-Z]{24})(?:&(.*))?$", re.I),
    re.compile("^(.+)(?:cfid=[^&]+&cftoken=[^&]+)(?:&(.*))?$", re.I),
    ]

def stripQuerySessionID(path):
    """These doctests are from IAURLCanonicalizerTest.java:

    >>> #base = "http://www.archive.org/index.html"
    >>> base = ""
    >>> str32id = "0123456789abcdefghijklemopqrstuv"
    >>> url = base + "?jsessionid=" + str32id
    >>> stripQuerySessionID(url)
    '?'

    Test that we don't strip if not 32 chars only.
    >>> url = base + "?jsessionid=" + str32id + '0'
    >>> stripQuerySessionID(url)
    '?jsessionid=0123456789abcdefghijklemopqrstuv0'

    Test what happens when followed by another key/value pair.
    >>> url = base + "?jsessionid=" + str32id + "&x=y"
    >>> stripQuerySessionID(url)
    '?x=y'

    Test what happens when followed by another key/value pair and
    prefixed by a key/value pair.
    >>> url = base + "?one=two&jsessionid=" + str32id + "&x=y"
    >>> stripQuerySessionID(url)
    '?one=two&x=y'

    Test what happens when prefixed by a key/value pair.
    >>> url = base + "?one=two&jsessionid=" + str32id
    >>> stripQuerySessionID(url)
    '?one=two&'

    Test aspsession.
    >>> url = base + "?aspsessionidABCDEFGH=" + "ABCDEFGHIJKLMNOPQRSTUVWX" + "&x=y"
    >>> stripQuerySessionID(url)
    '?x=y'

    Test archive phpsession.
    >>> url = base + "?phpsessid=" + str32id + "&x=y"
    >>> stripQuerySessionID(url)
    '?x=y'

    With prefix too.
    >>> url = base + "?one=two&phpsessid=" + str32id + "&x=y"
    >>> stripQuerySessionID(url)
    '?one=two&x=y'

    With only prefix
    >>> url = base + "?one=two&phpsessid=" + str32id
    >>> stripQuerySessionID(url)
    '?one=two&'

    Test sid.
    >>> url = base + "?" + "sid=9682993c8daa2c5497996114facdc805" + "&x=y";
    >>> stripQuerySessionID(url)
    '?x=y'

    Igor test.
    >>> url = base + "?" + "sid=9682993c8daa2c5497996114facdc805" + "&" + "jsessionid=" + str32id
    >>> stripQuerySessionID(url)
    '?'

    >>> url = "?CFID=1169580&CFTOKEN=48630702&dtstamp=22%2F08%2F2006%7C06%3A58%3A11"
    >>> stripQuerySessionID(url)
    '?dtstamp=22%2F08%2F2006%7C06%3A58%3A11'

    >>> url = "?CFID=12412453&CFTOKEN=15501799&dt=19_08_2006_22_39_28"
    >>> stripQuerySessionID(url)
    '?dt=19_08_2006_22_39_28'

    >>> url = "?CFID=14475712&CFTOKEN=2D89F5AF-3048-2957-DA4EE4B6B13661AB&r=468710288378&m=forgotten"
    >>> stripQuerySessionID(url)
    '?r=468710288378&m=forgotten'

    >>> url = "?CFID=16603925&CFTOKEN=2AE13EEE-3048-85B0-56CEDAAB0ACA44B8"
    >>> stripQuerySessionID(url)
    '?'

    >>> url = "?CFID=4308017&CFTOKEN=63914124&requestID=200608200458360%2E39414378"
    >>> stripQuerySessionID(url)
    '?requestID=200608200458360%2E39414378'

    """
    for pattern in _RES_QUERY_SESSIONID:
        m = pattern.match(path)
        if m:
            if m.group(2):
                path = m.group(1) + m.group(2)
            else:
                path = m.group(1)

    return path


# hostToSURT
#_______________________________________________________________________________
def hostToSURT(host):
    """This doctest comes from IAURLCanonicalizerTest.java:
    >>> hostToSURT("www.archive.org")
    'org,archive,www'
    """
    # TODO: ensure we DONT reverse IP addresses!
    parts = host.split('.')
    parts.reverse()
    return ','.join(parts)

# main()
#_______________________________________________________________________________
if __name__ == "__main__":
    import doctest
    doctest.testmod()

