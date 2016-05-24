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
    """
    for pattern in _RES_PATH_SESSIONID:
        m = pattern.match(path)
        if m:
            path = m.group(1) + m.group(3)

    return path


# stripQuerySessionID
#_______________________________________________________________________________
_RES_QUERY_SESSIONID = [
    re.compile("^(.*)(?:jsessionid=[0-9a-zA-Z]{32})(?:&(.*))?$", re.I),
    re.compile("^(.*)(?:phpsessid=[0-9a-zA-Z]{32})(?:&(.*))?$", re.I),
    re.compile("^(.*)(?:sid=[0-9a-zA-Z]{32})(?:&(.*))?$", re.I),
    re.compile("^(.*)(?:ASPSESSIONID[a-zA-Z]{8}=[a-zA-Z]{24})(?:&(.*))?$", re.I),
    re.compile("^(.*)(?:cfid=[^&]+&cftoken=[^&]+)(?:&(.*))?$", re.I),
    ]

def stripQuerySessionID(query):
    for pattern in _RES_QUERY_SESSIONID:
        m = pattern.match(query)
        if m:
            if m.group(2):
                query = m.group(1) + m.group(2)
            else:
                query = m.group(1)

    return query


# hostToSURT
#_______________________________________________________________________________
def hostToSURT(host):
    # TODO: ensure we DONT reverse IP addresses!
    parts = host.split('.')
    parts.reverse()
    return ','.join(parts)

