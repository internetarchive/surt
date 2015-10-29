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
"""
from __future__ import absolute_import

import surt.GoogleURLCanonicalizer
import surt.IAURLCanonicalizer


# canonicalize()
#_______________________________________________________________________________
def canonicalize(url, **options):
    """The input url is a handyurl instance
    """

    url = surt.GoogleURLCanonicalizer.canonicalize(url, **options)
    url = surt.IAURLCanonicalizer.canonicalize(url, **options)

    return url
