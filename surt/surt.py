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

def _as_canonicalizers(r, c):
    if isinstance(c, (tuple, list)):
        for e in c:
            _as_canonicalizers(r, e)
    elif isinstance(c, type):
        r.append(c.canonicalize)
    elif callable(c):
        r.append(c)
    elif hasattr(c, 'canonicalize'):
        r.append(c.canonicalize)
    else:
        raise TypeError('canonicalizer must either be callable or object'
                        ' with "canonicalize" method')
    return r

def _public_suffix(hurl, **options):
    hurl.host = hurl.getPublicSuffix()

class Transformer(object):
    def __init__(self, canonicalizer=None, surt=True, public_suffix=False,
                 **options):
        self.options = options
        if canonicalizer is None:
            canonicalizer = DefaultIAURLCanonicalizer.canonicalize
        self.canonicalizers = _as_canonicalizers([], canonicalizer)
        if public_suffix:
            self.canonicalizers.append(_public_suffix)
        if surt:
            if surt == 'ssurt':
                self.fmt = Format.SSURT(**options)
            else:
                self.fmt = Format.SURT(**options)
        else:
            self.fmt = Format.URI(**options)

    def _transform_bytes(self, url):
        if url.startswith(b"filedesc"):
            return url
        hurl = handyurl.parse(url)
        for canonicalizer in self.canonicalizers:
            canonicalizer(hurl, **self.options)
        return self.fmt.format(hurl)

    def transform(self, url):
        if not url:
            return "-"
        if isinstance(url, bytes):
            return self._transform_bytes(url)
        else:
            return self._transform_bytes(url.encode('utf-8')).decode('utf-8')

def surt(url, **options):
    transformer = Transformer(**options)
    return transformer.transform(url)
