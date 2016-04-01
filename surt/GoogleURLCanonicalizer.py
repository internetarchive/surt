#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

"""This is a python port of GoogleURLCanonicalizer.java:
http://archive-access.svn.sourceforge.net/viewvc/archive-access/trunk/archive-access/projects/archive-commons/src/main/java/org/archive/url/GoogleURLCanonicalizer.java?view=markup
"""

from __future__ import absolute_import

import re
import struct
import socket
import encodings.idna

from surt.handyurl import handyurl

try:
    from urllib.parse import quote_from_bytes, unquote_to_bytes
except:
    from urllib import quote as quote_from_bytes, unquote as unquote_to_bytes
from six import text_type, binary_type

# canonicalize()
#_______________________________________________________________________________
def canonicalize(url, **_ignored):
    url.hash = None
    if url.authUser:
        url.authUser = minimalEscape(url.authUser)
    if url.authPass:
        url.authPass = minimalEscape(url.authPass)
    if url.query:
        url.query = minimalEscape(url.query)

    if url.host:
        host = unescapeRepeatedly(url.host)
        try:
            host.decode('ascii')
        except UnicodeDecodeError:
            try:
                host = host.decode('utf-8', 'ignore').encode('idna')
            except ValueError:
                pass

        host = host.replace(b'..', b'.').strip(b'.')

        ip = attemptIPFormats(host)
        if ip:
            host = ip;
        else:
            host = escapeOnce(host.lower())

        url.host = host

    path = unescapeRepeatedly(url.path)
    if url.host:
        path = normalizePath(path)
    # else path is free-form sort of thing, not /directory/thing
    url.path = escapeOnce(path)

    return url

# normalizePath()
#_______________________________________________________________________________

def normalizePath(path):
    if not path:
        return b'/'

    #gives an empty trailing element if path ends with '/':
    paths       = path.split(b'/')
    keptPaths   = []
    first       = True

    for p in paths:
        if first:
            first = False
            continue
        elif b'.' == p:
            # skip
            continue
        elif b'..' == p:
            #pop the last path, if present:
            if len(keptPaths) > 0:
                keptPaths = keptPaths[:-1]
            else:
                # TODO: leave it? let's do for now...
                keptPaths.append(p)
        else:
            keptPaths.append(p)

    path = b'/'

    # If the path ends in '/', then the last element of keptPaths will be ''
    # Since we add a trailing '/' after the second-to-last element of keptPaths
    # in the for loop below, the trailing slash is preserved.
    numKept = len(keptPaths)
    if numKept > 0:
        for i in range(0, numKept-1):
            p = keptPaths[i]
            if len(p) > 0:
                #this will omit multiple slashes:
                path += p + b'/'
        path += keptPaths[numKept-1]

    return path

OCTAL_IP = re.compile(br"^(0[0-7]*)(\.[0-7]+)?(\.[0-7]+)?(\.[0-7]+)?$")
DECIMAL_IP = re.compile(br"^([1-9][0-9]*)(\.[0-9]+)?(\.[0-9]+)?(\.[0-9]+)?$")

# attemptIPFormats()
#_______________________________________________________________________________
def attemptIPFormats(host):
    if None == host:
        return None

    if host.isdigit():
        #mask hostname to lower four bytes to workaround issue with liveweb arc files
        return socket.inet_ntoa(
                struct.pack('>L', int(host) & 0xffffffff)).encode('ascii')
    else:
        m = DECIMAL_IP.match(host)
        if m:
            try:
                return socket.gethostbyname_ex(host)[2][0].encode('ascii')
            except (socket.gaierror, socket.herror):
                return None
        else:
            m = OCTAL_IP.match(host)
            if m:
                try:
                    return socket.gethostbyname_ex(host)[2][0].encode('ascii')
                except socket.gaierror:
                    return None

    return None


# minimalEscape()
#_______________________________________________________________________________
def minimalEscape(input):
    return escapeOnce(unescapeRepeatedly(input))

# escapeOnce()
#_______________________________________________________________________________
def escapeOnce(input):
    """escape everything outside of 32-128, except #"""
    if input:
        return quote_from_bytes(
                input, safe=b'''!"$&'()*+,-./:;<=>?@[\]^_`{|}~''').encode(
                        'ascii')
    else:
        return input


# unescapeRepeatedly()
#_______________________________________________________________________________
def unescapeRepeatedly(input):
    '''Argument may be str or bytes. Returns bytes.'''
    if None == input:
        return None

    while True:
        un = unquote_to_bytes(input)
        if un == input:
            return input
        input = un

