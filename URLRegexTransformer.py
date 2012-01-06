#!/usr/bin/env python

"""This is a python port of URLRegexTransformer.java:
http://archive-access.svn.sourceforge.net/viewvc/archive-access/trunk/archive-access/projects/archive-commons/src/main/java/org/archive/url/URLRegexTransformer.java?view=markup

The doctests are copied from IAURLCanonicalizerTest.java:
http://archive-access.svn.sourceforge.net/viewvc/archive-access/trunk/archive-access/projects/archive-commons/src/test/java/org/archive/url/URLRegexTransformerTest.java?view=markup
"""

import re

# stripPathSessionID
#_______________________________________________________________________________
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
    patterns = [re.compile("^(.*/)(\((?:[a-z]\([0-9a-z]{24}\))+\)/)([^\?]+\.aspx.*)$", re.I),
                re.compile("^(.*/)(\\([0-9a-z]{24}\\)/)([^\\?]+\\.aspx.*)$", re.I),
               ]

    for pattern in patterns:
        m = pattern.match(path)
        if m:
            path = m.group(1) + m.group(3)

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

    if 1 == len(parts):
        return host

    parts.reverse()

    return ','.join(parts)

# main()
#_______________________________________________________________________________
if __name__ == "__main__":
    import doctest
    doctest.testmod()

