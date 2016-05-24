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

from __future__ import absolute_import

import re
import tldextract

from six.moves.urllib.parse import urlsplit

from surt.URLRegexTransformer import hostToSURT

_RE_MULTIPLE_PROTOCOLS = re.compile(r'^(https?://)+')
_RE_HAS_PROTOCOL = re.compile("^([a-zA-Z][a-zA-Z0-9\+\-\.]*):")
_RE_SPACES = re.compile('[\n\r\t]')

class handyurl(object):
    """A python port of the archive-commons org.archive.url HandyURL class

    To simplify the surt module, we add the URLParser.parse method here,
    which makes the URLParser class unnecessary. handyurl becomes a thin
    wrapper around python's urlparse module.

    Init an empty class:
    >>> h = handyurl()

    Init with just a host:
    >>> h = handyurl(host='www.amazon.co.uk')

    This version of handyurl contains a field for last_delimiter, to allow
    a url to roundtrip through this class without modification. From the
    urlparse docs:
    "This [roundtripping] may result in a slightly different, but equivalent URL,
    if the URL that was parsed originally had unnecessary delimiters
    (for example, a ? with an empty query; the RFC states that these are equivalent)."
    We want the url http://www.google.com/? to work, since there is a test for
    it in the GoogleURLCanonicalizer class. Note, however, the IAURLCanonicalizer
    class strips empty queries.
    """
    DEFAULT_PORT = None

    # init
    #___________________________________________________________________________
    def __init__(self, scheme=None, authUser=None, authPass=None,
                 host=None, port=DEFAULT_PORT, path=None,
                 query=None, hash=None, last_delimiter=None):
        self.scheme   = scheme
        self.authUser = authUser
        self.authPass = authPass
        self.host     = host
        self.port     = port
        self.path     = path
        self.query    = query
        self.hash     = hash
        self.last_delimiter = last_delimiter #added in python version

    # parse() classmethod
    #___________________________________________________________________________
    @classmethod
    def parse(cls, url):
        u"""This method was in the java URLParser class, but we don't need
        a whole class to parse a url, when we can just use python's urlparse.

        """
        # Note RE_SPACES does not match regular space (0x20). That is,
        # regular spaces are removed at head and tail, but not in the middle.
        # There's a test case for GoogleURLCanonicalizer.canonicalize that
        # asserts this behavior.
        url = url.strip()
        url = _RE_SPACES.sub('', url)

        url = cls.addDefaultSchemeIfNeeded(url)

        #From Tymm: deal with http://https/order.1and1.com
        url = _RE_MULTIPLE_PROTOCOLS.sub(lambda m: m.group(1), url)

        """The java code seems to use this regex:
        re.compile("^(([a-zA-Z][a-zA-Z0-9\+\-\.]*):)?((//([^/?#]*))?([^?#]*)(\?([^#]*))?)?(#(.*))?")
        """
        o = urlsplit(url)

        scheme   = o.scheme   or None
        query    = o.query    or None
        fragment = o.fragment or None

        """Deal with hostnames that end with ':' without being followed by a port number"""
        if o.netloc.endswith(':'):
            o = o._replace(netloc=o.netloc.rstrip(':'))
        port     = o.port     or None

        hostname = o.hostname or None
        path     = o.path     or None

        if scheme.startswith('http'):
            #deal with "http:////////////////www.vikings.com"
            if hostname is None and path is not None:
                parts    = path.lstrip('/').partition('/')
                hostname = parts[0]
                path     = '/'+parts[2]

        h = cls(scheme = scheme,
                host   = hostname,
                path   = path,
                query  = query,
                hash   = fragment,
                port   = port,
               )

        #See note at top about last_delimiter
        if url.endswith('?') and None == h.query:
            h.last_delimiter = '?'

        return h

    # addDefaultSchemeIfNeeded()
    #___________________________________________________________________________
    """copied from URLParser.java"""
    @classmethod
    def addDefaultSchemeIfNeeded(cls, url):
        if not url:
            return url

        ###noah: accept anything that looks like it starts with a scheme:
        if _RE_HAS_PROTOCOL.match(url):
            return url
        else:
            return "http://"+url

    # geturl()
    #___________________________________________________________________________
    def geturl(self):
        """urlparse.ParseResult has a geturl() method, so we have one too.
        Nicer than typing the java method name!
        """
        return self.getURLString()

    # getURLString()
    #___________________________________________________________________________
    def getURLString(self,
                     surt=False,
                     public_suffix=False,
                     trailing_comma=False,
                     **options):

        s = self.scheme + ':'

        hostSrc = self.host
        if hostSrc:
            if public_suffix:
                hostSrc = self.getPublicSuffix()
            if surt:
                hostSrc = hostToSURT(hostSrc)

        if hostSrc:
            if self.scheme != 'dns':
                s += '//'

            if surt:
                s += "("

            if self.authUser:
                s += self.authUser
                if self.authPass:
                    s += self.authPass
                s += '@'

            s += hostSrc

            if self.port != self.DEFAULT_PORT:
                s += ":%d" % self.port

            if surt:
                if trailing_comma:
                    s += ','
                s += ')'

        if self.path:
            s += self.path
        elif self.query is not None or self.hash is not None:
            #must have '/' with query or hash:
            s += '/'

        if None != self.query:
            s += '?' + self.query
        if None != self.hash:
            s += '#' + self.hash

        if None != self.last_delimiter:
            s += self.last_delimiter

        return s

    # getPublicSuffix
    #___________________________________________________________________________
    def getPublicSuffix(self):
        """Uses the tldextract module to get the public suffix via the
        Public Suffix List.
        """
        return tldextract.extract(self.host).registered_domain

    # getPublicPrefix
    #___________________________________________________________________________
    def getPublicPrefix(self):
        """Uses the tldextract module to get the subdomain, using the
        Public Suffix List.
        """
        return tldextract.extract(self.host).subdomain

    # repr
    #___________________________________________________________________________
    # commented out because of http://bugs.python.org/issue5876
    # "__repr__ returning unicode doesn't work when called implicitly"
    #def __repr__(self):
    #    return u"""handyurl(scheme=%s, authUser=%s, authPass=%s, host=%s, port=%s, path=%s, query=%s, hash=%s)""".encode('utf-8') % (self.scheme, self.authUser, self.authPass, self.host, self.port, self.path, self.query, self.hash)

