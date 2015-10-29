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

from six.moves.urllib.parse import quote, unquote
from six import text_type, binary_type

# unescapeRepeatedly()
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
        hostE = unescapeRepeatedly(url.host)

        # if the host was an ascii string of percent-encoded bytes that represent
        # non-ascii unicode chars, then promote hostE from str to unicode.
        # e.g. "http://www.t%EF%BF%BD%04.82.net/", which contains the unicode replacement char
        if isinstance(hostE, binary_type):
            try:
                hostE.decode('ascii')
            except UnicodeDecodeError:
                hostE = hostE.decode('utf-8', 'ignore')


        host = None
        try:
            # Note: I copied the use of the ToASCII(hostE) from
            # the java code. This function implements RFC3490, which
            # requires that each component of the hostname (i.e. each label)
            # be encodeced separately, and doesn't work correctly with
            # full hostnames. So use 'idna' encoding instead.
            #host = encodings.idna.ToASCII(hostE)
            host = hostE.encode('idna').decode('utf-8')
        except ValueError:
            host = hostE

        host = host.replace('..', '.').strip('.')

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
        return '/'

    #gives an empty trailing element if path ends with '/':
    paths       = path.split('/')
    keptPaths   = []
    first       = True

    for p in paths:
        if first:
            first = False
            continue
        elif '.' == p:
            # skip
            continue
        elif '..' == p:
            #pop the last path, if present:
            if len(keptPaths) > 0:
                keptPaths = keptPaths[:-1]
            else:
                # TODO: leave it? let's do for now...
                keptPaths.append(p)
        else:
            keptPaths.append(p)

    path = '/'

    # If the path ends in '/', then the last element of keptPaths will be ''
    # Since we add a trailing '/' after the second-to-last element of keptPaths
    # in the for loop below, the trailing slash is preserved.
    numKept = len(keptPaths)
    if numKept > 0:
        for i in range(0, numKept-1):
            p = keptPaths[i]
            if len(p) > 0:
                #this will omit multiple slashes:
                path += p + '/'
        path += keptPaths[numKept-1]

    return path

OCTAL_IP = re.compile(r"^(0[0-7]*)(\.[0-7]+)?(\.[0-7]+)?(\.[0-7]+)?$")
DECIMAL_IP = re.compile(r"^([1-9][0-9]*)(\.[0-9]+)?(\.[0-9]+)?(\.[0-9]+)?$")

# attemptIPFormats()
#_______________________________________________________________________________
def attemptIPFormats(host):
    if None == host:
        return None

    if host.isdigit():
        #mask hostname to lower four bytes to workaround issue with liveweb arc files
        return socket.inet_ntoa(struct.pack('>L', int(host) & 0xffffffff))
    else:
        m = DECIMAL_IP.match(host)
        if m:
            try:
                return socket.gethostbyname_ex(host)[2][0]
            except (socket.gaierror, socket.herror):
                return None
        else:
            m = OCTAL_IP.match(host)
            if m:
                try:
                    return socket.gethostbyname_ex(host)[2][0]
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
        # If input is a unicode type, we need to chose an encoding before
        # percent encoding, since different encodings of the same unicode
        # characters will result in different surts.
        # We will use utf-8 for consistency.
        if isinstance(input, text_type):
            input = input.encode('utf-8')
        return quote(input, """!"$&'()*+,-./:;<=>?@[\]^_`{|}~""")
    else:
        return input


# unescapeRepeatedly()
#_______________________________________________________________________________
def unescapeRepeatedly(input):
    if None == input:
        return None

    while True:
        un = unquote(input)
        if un == input:
            return input
        input = un

