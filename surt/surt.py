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
    if not url:
        return "-"

    if url.startswith("filedesc"):
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

    if not options.get('with_scheme'):
        parenIdx = key.find('(')
        if -1 == parenIdx:
            return url #something very wrong
        return key[parenIdx+1:]
    else:
        return key

