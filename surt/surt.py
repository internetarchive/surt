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

import re
from functools import partial

from .handyurl import handyurl
from ._canonicalizer import DefaultIAURLCanonicalizer
from . import _surtformat as Format

class CompositeCanonicalizer(object):
    def __init__(self, canonicalizers):
        self.canonicalizers = [
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
        raise AttributeError('canonicalizer must either be callable or have'
                             ' "canonicalizer" method')

def surt(url, **options):
    if not url:
        return "-"
    if isinstance(url, bytes):
        return _surt_bytes(url, **options)
    else:
        return _surt_bytes(url.encode('utf-8'), **options).decode('utf-8')

def _surt_bytes(url, canonicalizer=None, surt=True, public_suffix=False, **options):
    if url.startswith(b"filedesc"):
        return url

    if canonicalizer is None:
        canonicalizer = DefaultIAURLCanonicalizer.canonicalize
    else:
        if isinstance(canonicalizer, (list, tuple)):
            canonicalizer = CompositeCanonicalizer(canonicalizer)
        elif (not hasattr(canonicalizer, '__call__') and
              hasattr(canonicalizer, 'canonicalize')):
            canonicalizer = canonicalizer.canonicalize

    hurl = canonicalizer(handyurl.parse(url), **options)
    if public_suffix and hurl.host:
        # probably we can inline handyurl.getPublicSuffix() here and remove the method.
        hurl.host = hurl.getPublicSuffix()

    fmt = Format.SURT if surt else Format.URL
    return fmt(**options).format(hurl)
