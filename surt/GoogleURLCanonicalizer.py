#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This is a python port of GoogleURLCanonicalizer.java:
http://archive-access.svn.sourceforge.net/viewvc/archive-access/trunk/archive-access/projects/archive-commons/src/main/java/org/archive/url/GoogleURLCanonicalizer.java?view=markup

The doctests are copied from GoogleURLCanonicalizerTest.java:
http://archive-access.svn.sourceforge.net/viewvc/archive-access/trunk/archive-access/projects/archive-commons/src/test/java/org/archive/url/GoogleURLCanonicalizerTest.java?view=markup
"""

import re
import struct
import socket
import encodings.idna
from handyurl import handyurl
from urllib import quote, unquote


# unescapeRepeatedly()
#_______________________________________________________________________________
def canonicalize(url):
    """
    >>> canonicalize(handyurl.parse("http://host/%25%32%35")).getURLString()
    'http://host/%25'
    >>> canonicalize(handyurl.parse("http://host/%25%32%35%25%32%35")).getURLString()
    'http://host/%25%25'
    >>> canonicalize(handyurl.parse("http://host/%2525252525252525")).getURLString()
    'http://host/%25'
    >>> canonicalize(handyurl.parse("http://host/asdf%25%32%35asd")).getURLString()
    'http://host/asdf%25asd'
    >>> canonicalize(handyurl.parse("http://host/%%%25%32%35asd%%")).getURLString()
    'http://host/%25%25%25asd%25%25'
    >>> canonicalize(handyurl.parse("http://www.google.com/")).getURLString()
    'http://www.google.com/'
    >>> canonicalize(handyurl.parse("http://%31%36%38%2e%31%38%38%2e%39%39%2e%32%36/%2E%73%65%63%75%72%65/%77%77%77%2E%65%62%61%79%2E%63%6F%6D/")).getURLString()
    'http://168.188.99.26/.secure/www.ebay.com/'
    >>> canonicalize(handyurl.parse("http://195.127.0.11/uploads/%20%20%20%20/.verify/.eBaysecure=updateuserdataxplimnbqmn-xplmvalidateinfoswqpcmlx=hgplmcx/")).getURLString()
    'http://195.127.0.11/uploads/%20%20%20%20/.verify/.eBaysecure=updateuserdataxplimnbqmn-xplmvalidateinfoswqpcmlx=hgplmcx/'
    >>> canonicalize(handyurl.parse("http://host%23.com/%257Ea%2521b%2540c%2523d%2524e%25f%255E00%252611%252A22%252833%252944_55%252B")).getURLString()
    'http://host%23.com/~a!b@c%23d$e%25f^00&11*22(33)44_55+'
    >>> canonicalize(handyurl.parse("http://3279880203/blah")).getURLString()
    'http://195.127.0.11/blah'
    >>> canonicalize(handyurl.parse("http://www.google.com/blah/..")).getURLString()
    'http://www.google.com/'
    >>> canonicalize(handyurl.parse("www.google.com/")).getURLString()
    'http://www.google.com/'
    >>> canonicalize(handyurl.parse("www.google.com")).getURLString()
    'http://www.google.com/'
    >>> canonicalize(handyurl.parse("http://www.evil.com/blah#frag")).getURLString()
    'http://www.evil.com/blah'
    >>> canonicalize(handyurl.parse("http://www.GOOgle.com/")).getURLString()
    'http://www.google.com/'
    >>> canonicalize(handyurl.parse("http://www.google.com.../")).getURLString()
    'http://www.google.com/'

    #This works but the newline in the docstring messes up doctest
    #>>> canonicalize(handyurl.parse("http://www.google.com/foo\tbar\rbaz\n2")).getURLString()
    #'http://www.google.com/foobarbaz2'

    >>> canonicalize(handyurl.parse("http://www.google.com/q?")).getURLString()
    'http://www.google.com/q?'
    >>> canonicalize(handyurl.parse("http://www.google.com/q?r?")).getURLString()
    'http://www.google.com/q?r?'
    >>> canonicalize(handyurl.parse("http://www.google.com/q?r?s")).getURLString()
    'http://www.google.com/q?r?s'
    >>> canonicalize(handyurl.parse("http://evil.com/foo#bar#baz")).getURLString()
    'http://evil.com/foo'
    >>> canonicalize(handyurl.parse("http://evil.com/foo;")).getURLString()
    'http://evil.com/foo;'
    >>> canonicalize(handyurl.parse("http://evil.com/foo?bar;")).getURLString()
    'http://evil.com/foo?bar;'

    #This test case differs from the Java version. The Java version returns
    #'http://%01%80.com/' for this case. If idna/punycode encoding of a hostname
    #is not possible, the python version encodes unicode domains as utf-8 before
    #percent encoding, so we get 'http://%01%C2%80.com/'
    >>> print canonicalize(handyurl.parse(u"http://\u0001\u0080.com/")).getURLString()
    http://%01%C2%80.com/

    #Add these unicode tests:
    >>> print canonicalize(handyurl.parse(u'B\xfccher.ch:8080')).getURLString()
    http://xn--bcher-kva.ch:8080/
    >>> url = '☃.com'.decode('utf-8') #doctest has trouble with utf-8 encoding
    >>> print canonicalize(handyurl.parse(url)).getURLString()
    http://xn--n3h.com/

    #Add these percent-encoded unicode tests
    >>> canonicalize(handyurl.parse("http://www.t%EF%BF%BD%04.82.net/")).getURLString()
    'http://www.t%EF%BF%BD%04.82.net/'

    >>> canonicalize(handyurl.parse("http://notrailingslash.com")).getURLString()
    'http://notrailingslash.com/'
    >>> canonicalize(handyurl.parse("http://www.gotaport.com:1234/")).getURLString()
    'http://www.gotaport.com:1234/'
    >>> canonicalize(handyurl.parse("  http://www.google.com/  ")).getURLString()
    'http://www.google.com/'
    >>> canonicalize(handyurl.parse("http:// leadingspace.com/")).getURLString()
    'http://%20leadingspace.com/'
    >>> canonicalize(handyurl.parse("http://%20leadingspace.com/")).getURLString()
    'http://%20leadingspace.com/'
    >>> canonicalize(handyurl.parse("%20leadingspace.com/")).getURLString()
    'http://%20leadingspace.com/'
    >>> canonicalize(handyurl.parse("https://www.securesite.com/")).getURLString()
    'https://www.securesite.com/'
    >>> canonicalize(handyurl.parse("http://host.com/ab%23cd")).getURLString()
    'http://host.com/ab%23cd'
    >>> canonicalize(handyurl.parse("http://host.com//twoslashes?more//slashes")).getURLString()
    'http://host.com/twoslashes?more//slashes'
    """

    url.hash = None
    if url.authUser:
        url.authUser = minimalEscape(url.authUser)
    if url.authPass:
        url.authPass = minimalEscape(url.authPass)
    if url.query:
        url.query = minimalEscape(url.query)

    hostE = unescapeRepeatedly(url.host)

    # if the host was an ascii string of percent-encoded bytes that represent
    # non-ascii unicode chars, then promote hostE from str to unicode.
    # e.g. "http://www.t%EF%BF%BD%04.82.net/", which contains the unicode replacement char
    if isinstance(hostE, str):
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
        host = hostE.encode('idna')
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
    url.path = escapeOnce(normalizePath(path))

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

# attemptIPFormats()
#_______________________________________________________________________________
def attemptIPFormats(host):
    """
    The doctests are copied from GoogleURLCanonicalizerTest.java:

    >>> attemptIPFormats(None)
    >>> attemptIPFormats("www.foo.com") #returns None
    >>> attemptIPFormats("127.0.0.1")
    '127.0.0.1'
    >>> attemptIPFormats("017.0.0.1")
    '15.0.0.1'
    >>> attemptIPFormats("168.188.99.26")
    '168.188.99.26'
    >>> attemptIPFormats("10.0.258") #java version returns null, ours returns the correct ipv4
    '10.0.1.2'
    >>> attemptIPFormats("1.2.3.256") #returns None

    ARC files from the wayback machine's liveweb proxy contain numeric
    hostnames > 2^32 for some reason. We'll copy the behavior of the java code.
    >>> attemptIPFormats("39024579298")
    '22.11.210.226'
    """

    OCTAL_IP   = re.compile("^(0[0-7]*)(\.[0-7]+)?(\.[0-7]+)?(\.[0-7]+)?$")
    DECIMAL_IP = re.compile("^([1-9][0-9]*)(\.[0-9]+)?(\.[0-9]+)?(\.[0-9]+)?$")

    if None == host:
        return None

    if re.match("^\d+$", host):
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
        if isinstance(input, unicode):
            input = input.encode('utf-8')
        return quote(input, """!"$&'()*+,-./:;<=>?@[\]^_`{|}~""")
    else:
        return input


# unescapeRepeatedly()
#_______________________________________________________________________________
def unescapeRepeatedly(input):
    """
    The doctests are copied from GoogleURLCanonicalizerTest.java:

    >>> unescapeRepeatedly("%!A%21%21%25")
    '%!A!!%'
    >>> unescapeRepeatedly("%")
    '%'
    >>> unescapeRepeatedly("%2")
    '%2'
    >>> unescapeRepeatedly("%25")
    '%'
    >>> unescapeRepeatedly("%25%")
    '%%'
    >>> unescapeRepeatedly("%2525")
    '%'
    >>> unescapeRepeatedly("%252525")
    '%'
    >>> unescapeRepeatedly("%25%32%35")
    '%'
    """
    if None == input:
        return None

    while True:
        un = unquote(input)
        if un == input:
            return input
        input = un

# main()
#_______________________________________________________________________________
if __name__ == "__main__":
    import doctest
    doctest.testmod()
