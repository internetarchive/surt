# -*- coding: utf-8 -*-

import surt
from surt import handyurl
import surt._canonicalizer as canonicalizer

import pytest

@pytest.mark.parametrize("url_in,url_out", [
    ("http://www.alexa.com/", 'http://alexa.com/'),
    ("http://archive.org/index.html", 'http://archive.org/index.html'),
    ("http://archive.org/index.html?", 'http://archive.org/index.html'),
    ("http://archive.org/index.html?a=b", 'http://archive.org/index.html?a=b'),
    ("http://archive.org/index.html?b=b&a=b", 'http://archive.org/index.html?a=b&b=b'),
    ("http://archive.org/index.html?b=a&b=b&a=b", 'http://archive.org/index.html?a=b&b=a&b=b'),
    ("http://www34.archive.org/index.html?b=a&b=b&a=b", 'http://archive.org/index.html?a=b&b=a&b=b')
])
def test_DefaultIAURLCanonicalizer(url_in, url_out):
    hurl = handyurl.parse(url_in)
    surt.DefaultIAURLCanonicalizer.canonicalize(hurl)
    assert hurl.geturl() == url_out

def test_GoogleURLCanonicalizer():
    # The tests are copied from GoogleURLCanonicalizerTest.java
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://host/%25%32%35")).getURLString() == 'http://host/%25'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://host/%25%32%35%25%32%35")).getURLString() == 'http://host/%25%25'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://host/%2525252525252525")).getURLString() == 'http://host/%25'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://host/asdf%25%32%35asd")).getURLString() == 'http://host/asdf%25asd'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://host/%%%25%32%35asd%%")).getURLString() == 'http://host/%25%25%25asd%25%25'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://www.google.com/")).getURLString() == 'http://www.google.com/'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://%31%36%38%2e%31%38%38%2e%39%39%2e%32%36/%2E%73%65%63%75%72%65/%77%77%77%2E%65%62%61%79%2E%63%6F%6D/")).getURLString() == 'http://168.188.99.26/.secure/www.ebay.com/'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://195.127.0.11/uploads/%20%20%20%20/.verify/.eBaysecure=updateuserdataxplimnbqmn-xplmvalidateinfoswqpcmlx=hgplmcx/")).getURLString() == 'http://195.127.0.11/uploads/%20%20%20%20/.verify/.eBaysecure=updateuserdataxplimnbqmn-xplmvalidateinfoswqpcmlx=hgplmcx/'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://host%23.com/%257Ea%2521b%2540c%2523d%2524e%25f%255E00%252611%252A22%252833%252944_55%252B")).getURLString() == 'http://host%23.com/~a!b@c%23d$e%25f^00&11*22(33)44_55+'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://3279880203/blah")).getURLString() == 'http://195.127.0.11/blah'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://www.google.com/blah/..")).getURLString() == 'http://www.google.com/'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("www.google.com/")).getURLString() == 'http://www.google.com/'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("www.google.com")).getURLString() == 'http://www.google.com/'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://www.evil.com/blah#frag")).getURLString() == 'http://www.evil.com/blah'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://www.GOOgle.com/")).getURLString() == 'http://www.google.com/'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://www.google.com.../")).getURLString() == 'http://www.google.com/'

    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://www.google.com/foo\tbar\rbaz\n2")).getURLString() == 'http://www.google.com/foobarbaz2'

    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://www.google.com/q?")).getURLString() == 'http://www.google.com/q?'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://www.google.com/q?r?")).getURLString() == 'http://www.google.com/q?r?'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://www.google.com/q?r?s")).getURLString() == 'http://www.google.com/q?r?s'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://evil.com/foo#bar#baz")).getURLString() == 'http://evil.com/foo'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://evil.com/foo;")).getURLString() == 'http://evil.com/foo;'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://evil.com/foo?bar;")).getURLString() == 'http://evil.com/foo?bar;'

    #This test case differs from the Java version. The Java version returns
    #'http://%01%80.com/' for this case. If idna/punycode encoding of a hostname
    #is not possible, the python version encodes unicode domains as utf-8 before
    #percent encoding, so we get 'http://%01%C2%80.com/'
    # assert print(canonicalize(handyurl.parse(u"http://\u0001\u0080.com/")).getURLString()) http://%01%C2%80.com/
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse(u"http://\u0001\u0080.com/")).getURLString() == 'http://%01%C2%80.com/'

    #Add these unicode tests:
    # assert print(canonicalize(handyurl.parse(u'B\xfccher.ch:8080')).getURLString()) http://xn--bcher-kva.ch:8080/
    # assert print(canonicalize(handyurl.parse('☃.com')).getURLString()) == http://xn--n3h.com/
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse(u'B\xfccher.ch:8080')).getURLString() == 'http://xn--bcher-kva.ch:8080/'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse('☃.com')).getURLString() == 'http://xn--n3h.com/'

    #Add these percent-encoded unicode tests
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://www.t%EF%BF%BD%04.82.net/")).getURLString() == 'http://www.t%EF%BF%BD%04.82.net/'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://notrailingslash.com")).getURLString() == 'http://notrailingslash.com/'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://www.gotaport.com:1234/")).getURLString() == 'http://www.gotaport.com:1234/'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("  http://www.google.com/  ")).getURLString() == 'http://www.google.com/'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http:// leadingspace.com/")).getURLString() == 'http://%20leadingspace.com/'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://%20leadingspace.com/")).getURLString() == 'http://%20leadingspace.com/'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("%20leadingspace.com/")).getURLString() == 'http://%20leadingspace.com/'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("https://www.securesite.com/")).getURLString() == 'https://www.securesite.com/'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://host.com/ab%23cd")).getURLString() == 'http://host.com/ab%23cd'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("http://host.com//twoslashes?more//slashes")).getURLString() == 'http://host.com/twoslashes?more//slashes'
    assert surt.GoogleURLCanonicalizer.canonicalize(handyurl.parse("mailto:foo@example.com")).getURLString() == 'mailto:foo@example.com'

def test_IAURLCanonicalizer():
    # These tests are from IAURLCanonicalizerTest.java
    assert surt.IAURLCanonicalizer.canonicalize(handyurl.parse("http://ARCHIVE.ORG/")).getURLString() == 'http://archive.org/'
    assert surt.IAURLCanonicalizer.canonicalize(handyurl.parse("http://www.archive.org:80/")).getURLString() == 'http://archive.org/'
    assert surt.IAURLCanonicalizer.canonicalize(handyurl.parse("https://www.archive.org:80/")).getURLString() == 'https://archive.org:80/'
    assert surt.IAURLCanonicalizer.canonicalize(handyurl.parse("http://www.archive.org:443/")).getURLString() == 'http://archive.org:443/'
    assert surt.IAURLCanonicalizer.canonicalize(handyurl.parse("https://www.archive.org:443/")).getURLString() == 'https://archive.org/'
    assert surt.IAURLCanonicalizer.canonicalize(handyurl.parse("http://www.archive.org/big/")).getURLString() == 'http://archive.org/big'
    assert surt.IAURLCanonicalizer.canonicalize(handyurl.parse("dns:www.archive.org")).getURLString() == 'dns:www.archive.org'

def test_options():
    assert surt.IAURLCanonicalizer.canonicalize(handyurl.parse('http://example.com/foo?X=Y')).getURLString() == 'http://example.com/foo?x=y'
    assert surt.IAURLCanonicalizer.canonicalize(handyurl.parse('http://example.com/foo?X=Y'), query_lowercase=False).getURLString() == 'http://example.com/foo?X=Y'
    assert surt.DefaultIAURLCanonicalizer.canonicalize(handyurl.parse('http://example.com/foo?X=Y')).getURLString() == 'http://example.com/foo?x=y'
    assert surt.DefaultIAURLCanonicalizer.canonicalize(handyurl.parse('http://example.com/foo?X=Y'), query_lowercase=False).getURLString() == 'http://example.com/foo?X=Y'

# direct test of internal canonicalization functions

def test_attemptIPFormats():
    # The tests are copied from GoogleURLCanonicalizerTest.java
    assert canonicalizer.attemptIPFormats(None) is None
    assert canonicalizer.attemptIPFormats(b"www.foo.com") is None
    assert canonicalizer.attemptIPFormats(b"127.0.0.1") == b'127.0.0.1'
    assert canonicalizer.attemptIPFormats(b"017.0.0.1") == b'15.0.0.1'
    assert canonicalizer.attemptIPFormats(b"168.188.99.26") == b'168.188.99.26'
    #java version returns null, ours returns the correct ipv4
    assert canonicalizer.attemptIPFormats(b"10.0.258") == b'10.0.1.2'
    assert canonicalizer.attemptIPFormats(b"1.2.3.256") is None #returns None

    # ARC files from the wayback machine's liveweb proxy contain numeric
    # hostnames > 2^32 for some reason. We'll copy the behavior of the java code.
    assert canonicalizer.attemptIPFormats(b"39024579298") == b'22.11.210.226'

def test_unescapeRepeatedly():
    # The tests are copied from GoogleURLCanonicalizerTest.java
    assert canonicalizer.unescapeRepeatedly(b"%!A%21%21%25") == b'%!A!!%'
    assert canonicalizer.unescapeRepeatedly(b"%") == b'%'
    assert canonicalizer.unescapeRepeatedly(b"%2") == b'%2'
    assert canonicalizer.unescapeRepeatedly(b"%25") == b'%'
    assert canonicalizer.unescapeRepeatedly(b"%25%") == b'%%'
    assert canonicalizer.unescapeRepeatedly(b"%2525") == b'%'
    assert canonicalizer.unescapeRepeatedly(b"%252525") == b'%'
    assert canonicalizer.unescapeRepeatedly(b"%25%32%35") == b'%'

@pytest.mark.parametrize("query_in,query_out", [
    (None, None),
    (b"", b""),
    (b"a", b"a"),
    (b"ab", b"ab"),
    (b"a=1", b"a=1"),
    (b"ab=1", b"ab=1"),
    (b"a=1&", b"&a=1"),
    (b"a=1&b=1", b"a=1&b=1"),
    (b"b=1&a=1", b"a=1&b=1"),
    (b"a=a&a=a", b"a=a&a=a"),
    (b"a=b&a=a", b"a=a&a=b"),
    (b"b=b&a=b&b=a&a=a", b"a=a&a=b&b=a&b=b")
])
def test_alphaReorderQuery(query_in, query_out):
    # These tests are from IAURLCanonicalizerTest.java
    assert canonicalizer.alphaReorderQuery(query_in) == query_out

@pytest.mark.parametrize("host_in,host_out", [
    (b"foo.com", b"foo.com"),
    (b"www.foo.com", b"foo.com"),
    (b"www2foo.com", b"www2foo.com"),
    (b"www2.www2foo.com", b"www2foo.com")
])
def test_massageHost(host_in, host_out):
    assert canonicalizer.massageHost(host_in) == host_out

@pytest.mark.parametrize("scheme_in,port_out", [
    (b"foo", 0),
    (b"http", 80),
    (b"https", 443)
])
def test_getDefaultPort(scheme_in, port_out):
    assert canonicalizer.getDefaultPort(scheme_in) == port_out

def test_stripPathSessionID():
    # These tests are from IAURLCanonicalizerTest.java
    # Check ASP_SESSIONID2:
    assert canonicalizer.stripPathSessionID(b"/(S(4hqa0555fwsecu455xqckv45))/mileg.aspx") == b'/mileg.aspx'

    # Check ASP_SESSIONID2 (again):
    assert canonicalizer.stripPathSessionID(b"/(4hqa0555fwsecu455xqckv45)/mileg.aspx") == b'/mileg.aspx'

    # Check ASP_SESSIONID3:
    assert canonicalizer.stripPathSessionID(b"/(a(4hqa0555fwsecu455xqckv45)S(4hqa0555fwsecu455xqckv45)f(4hqa0555fwsecu455xqckv45))/mileg.aspx?page=sessionschedules") == b'/mileg.aspx?page=sessionschedules'

    # '@' in path:
    assert canonicalizer.stripPathSessionID(b"/photos/36050182@N05/") == b'/photos/36050182@N05/'


@pytest.mark.parametrize("url_in,url_out", [
    ("?jsessionid={0}", "?"),
    # Test that we don't strip if not 32 chars only.
    ("?jsessionid={0}0", "?jsessionid={0}0"),
    # Test what happens when followed by another key/value pair.
    ("?jsessionid={0}&x=y", "?x=y"),
    # Test what happens when followed by another key/value pair and
    # prefixed by a key/value pair.
    ("?one=two&jsessionid={0}&x=y", '?one=two&x=y'),
    # Test what happens when prefixed by a key/value pair.
    ("?one=two&jsessionid={0}", '?one=two&'),

    # Test aspsession.
    ("?aspsessionidABCDEFGH=" + "ABCDEFGHIJKLMNOPQRSTUVWX" + "&x=y", "?x=y"),

    # Test archive phpsession.
    ("?phpsessid={0}&x=y", "?x=y"),
    # With prefix too.
    ("?one=two&phpsessid={0}&x=y", "?one=two&x=y"),
    # With only prefix
    ("?one=two&phpsessid={0}", "?one=two&"),

    # Test sid.
    ("?" + "sid=9682993c8daa2c5497996114facdc805" + "&x=y", "?x=y"),
    # Igor test.
    ("?" + "sid=9682993c8daa2c5497996114facdc805" + "&" + "jsessionid={0}", "?"),
])
def test_stripQuerySessionID(url_in, url_out):
    #base = "http://www.archive.org/index.html"
    base = b""
    str32id = "0123456789abcdefghijklemopqrstuv"

    url = base + url_in.format(str32id).encode('utf-8')
    expected = base + url_out.format(str32id).encode('utf-8')

    assert canonicalizer.stripQuerySessionID(url) == expected

@pytest.mark.parametrize("url_in,url_out", [
    ("?CFID=1169580&CFTOKEN=48630702&dtstamp=22%2F08%2F2006%7C06%3A58%3A11",
     '?dtstamp=22%2F08%2F2006%7C06%3A58%3A11'),
    ("?CFID=12412453&CFTOKEN=15501799&dt=19_08_2006_22_39_28",
     '?dt=19_08_2006_22_39_28'),
    ("?CFID=14475712&CFTOKEN=2D89F5AF-3048-2957-DA4EE4B6B13661AB&r=468710288378&m=forgotten",
     '?r=468710288378&m=forgotten'),
    ("?CFID=16603925&CFTOKEN=2AE13EEE-3048-85B0-56CEDAAB0ACA44B8", "?"),
    ("?CFID=4308017&CFTOKEN=63914124&requestID=200608200458360%2E39414378",
     '?requestID=200608200458360%2E39414378')
])
def test_stripQuerySessionID_CFID(url_in, url_out):
    base = b""
    url = base + url_in.encode('utf-8')
    expected = base + url_out.encode('utf-8')
    assert canonicalizer.stripQuerySessionID(url) == expected
