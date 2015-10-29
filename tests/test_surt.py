# -*- coding: utf-8 -*-

from __future__ import absolute_import

import surt
from surt import handyurl

def test_handyurl_parse():
    # These tests come from URLParserTest.java
    assert handyurl.parse("http://www.archive.org/index.html#foo").geturl() == 'http://www.archive.org/index.html#foo'
    assert handyurl.parse("http://www.archive.org/").geturl() == 'http://www.archive.org/'
    assert handyurl.parse("http://www.archive.org").geturl() == 'http://www.archive.org'
    assert handyurl.parse("http://www.archive.org?").geturl() == 'http://www.archive.org?' 
    assert handyurl.parse("http://www.archive.org:8080/index.html?query#foo").geturl() == 'http://www.archive.org:8080/index.html?query#foo'
    assert handyurl.parse("http://www.archive.org:8080/index.html?#foo").geturl() == 'http://www.archive.org:8080/index.html#foo'
    assert handyurl.parse("http://www.archive.org:8080?#foo").geturl() == 'http://www.archive.org:8080/#foo'
    assert handyurl.parse(u"http://bücher.ch:8080?#foo").geturl() == u'http://bücher.ch:8080/#foo'
    assert handyurl.parse(u"dns:bücher.ch").geturl() == u'dns:bücher.ch'
    # XXX assert print(handyurl.parse(u"http://bücher.ch:8080?#foo").geturl()) == http://b\xfccher.ch:8080/#foo 
    # XXX assert print(handyurl.parse(u"dns:bücher.ch").geturl()) == dns:b\xfccher.ch
    assert handyurl.parse(u"http://bücher.ch:8080?#foo").geturl() == u"http://b\xfccher.ch:8080/#foo"
    assert handyurl.parse(u"dns:bücher.ch").geturl() == u"dns:b\xfccher.ch"

    ###From Tymm:
    assert handyurl.parse("http:////////////////www.vikings.com").geturl() == 'http://www.vikings.com/'
    assert handyurl.parse("http://https://order.1and1.com").geturl() == 'https://order.1and1.com'

    ###From Common Crawl, host ends with ':' without a port number
    assert handyurl.parse("http://mineral.galleries.com:/minerals/silicate/chabazit/chabazit.htm").geturl() == 'http://mineral.galleries.com/minerals/silicate/chabazit/chabazit.htm'

    assert handyurl.parse("mailto:bot@archive.org").scheme == 'mailto'
    assert handyurl.parse("mailto:bot@archive.org").geturl() == 'mailto:bot@archive.org'

def test_getPublicSuffix():
    # These tests are based off the ones found in HandyURLTest.java
    assert handyurl(host='www.fool.com').getPublicSuffix() == 'fool.com'
    assert handyurl(host='www.amazon.co.uk').getPublicSuffix() == 'amazon.co.uk'
    assert handyurl(host='www.images.amazon.co.uk').getPublicSuffix() == 'amazon.co.uk'
    assert handyurl(host='funky-images.fancy.co.jp').getPublicSuffix() == 'fancy.co.jp'

def test_getPublicPrefix():
    # These tests are based off the ones found in HandyURLTest.java
    assert handyurl(host='www.fool.com').getPublicPrefix() == 'www'
    assert handyurl(host='www.amazon.co.uk').getPublicPrefix() == 'www'
    assert handyurl(host='www.images.amazon.co.uk').getPublicPrefix() == 'www.images'
    assert handyurl(host='funky-images.fancy.co.jp').getPublicPrefix() == 'funky-images'

def test_DefaultIAURLCanonicalizer():
    # These tests are from DefaultIAURLCanonicalizerTest.java
    assert surt.DefaultIAURLCanonicalizer.canonicalize(handyurl.parse("http://www.alexa.com/")).getURLString() == 'http://alexa.com/'
    assert surt.DefaultIAURLCanonicalizer.canonicalize(handyurl.parse("http://archive.org/index.html")).getURLString() == 'http://archive.org/index.html'
    assert surt.DefaultIAURLCanonicalizer.canonicalize(handyurl.parse("http://archive.org/index.html?")).getURLString() == 'http://archive.org/index.html'
    assert surt.DefaultIAURLCanonicalizer.canonicalize(handyurl.parse("http://archive.org/index.html?a=b")).getURLString() == 'http://archive.org/index.html?a=b'
    assert surt.DefaultIAURLCanonicalizer.canonicalize(handyurl.parse("http://archive.org/index.html?b=b&a=b")).getURLString() == 'http://archive.org/index.html?a=b&b=b'
    assert surt.DefaultIAURLCanonicalizer.canonicalize(handyurl.parse("http://archive.org/index.html?b=a&b=b&a=b")).getURLString() == 'http://archive.org/index.html?a=b&b=a&b=b'
    assert surt.DefaultIAURLCanonicalizer.canonicalize(handyurl.parse("http://www34.archive.org/index.html?b=a&b=b&a=b")).getURLString() == 'http://archive.org/index.html?a=b&b=a&b=b'

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

def test_attemptIPFormats():
    # The tests are copied from GoogleURLCanonicalizerTest.java
    assert surt.GoogleURLCanonicalizer.attemptIPFormats(None) is None
    assert surt.GoogleURLCanonicalizer.attemptIPFormats("www.foo.com") is None
    assert surt.GoogleURLCanonicalizer.attemptIPFormats("127.0.0.1") == '127.0.0.1'
    assert surt.GoogleURLCanonicalizer.attemptIPFormats("017.0.0.1") == '15.0.0.1'
    assert surt.GoogleURLCanonicalizer.attemptIPFormats("168.188.99.26") == '168.188.99.26'
    #java version returns null, ours returns the correct ipv4
    assert surt.GoogleURLCanonicalizer.attemptIPFormats("10.0.258") == '10.0.1.2'
    assert surt.GoogleURLCanonicalizer.attemptIPFormats("1.2.3.256") is None #returns None

    # ARC files from the wayback machine's liveweb proxy contain numeric
    # hostnames > 2^32 for some reason. We'll copy the behavior of the java code.
    assert surt.GoogleURLCanonicalizer.attemptIPFormats("39024579298") == '22.11.210.226'

def test_unescapeRepeatedly():
    # The tests are copied from GoogleURLCanonicalizerTest.java
    assert surt.GoogleURLCanonicalizer.unescapeRepeatedly("%!A%21%21%25") == '%!A!!%'
    assert surt.GoogleURLCanonicalizer.unescapeRepeatedly("%") == '%'
    assert surt.GoogleURLCanonicalizer.unescapeRepeatedly("%2") == '%2'
    assert surt.GoogleURLCanonicalizer.unescapeRepeatedly("%25") == '%'
    assert surt.GoogleURLCanonicalizer.unescapeRepeatedly("%25%") == '%%'
    assert surt.GoogleURLCanonicalizer.unescapeRepeatedly("%2525") == '%'
    assert surt.GoogleURLCanonicalizer.unescapeRepeatedly("%252525") == '%'
    assert surt.GoogleURLCanonicalizer.unescapeRepeatedly("%25%32%35") == '%'

def test_IAURLCanonicalizer():
    # These tests are from IAURLCanonicalizerTest.java
    assert surt.IAURLCanonicalizer.canonicalize(handyurl.parse("http://ARCHIVE.ORG/")).getURLString() == 'http://archive.org/'
    assert surt.IAURLCanonicalizer.canonicalize(handyurl.parse("http://www.archive.org:80/")).getURLString() == 'http://archive.org/'
    assert surt.IAURLCanonicalizer.canonicalize(handyurl.parse("https://www.archive.org:80/")).getURLString() == 'https://archive.org:80/'
    assert surt.IAURLCanonicalizer.canonicalize(handyurl.parse("http://www.archive.org:443/")).getURLString() == 'http://archive.org:443/'
    assert surt.IAURLCanonicalizer.canonicalize(handyurl.parse("https://www.archive.org:443/")).getURLString() == 'https://archive.org/'
    assert surt.IAURLCanonicalizer.canonicalize(handyurl.parse("http://www.archive.org/big/")).getURLString() == 'http://archive.org/big'
    assert surt.IAURLCanonicalizer.canonicalize(handyurl.parse("dns:www.archive.org")).getURLString() == 'dns:www.archive.org'

def test_alphaReorderQuery():
    # These tests are from IAURLCanonicalizerTest.java
    assert surt.IAURLCanonicalizer.alphaReorderQuery(None) is None
    assert surt.IAURLCanonicalizer.alphaReorderQuery("") == ''
    assert surt.IAURLCanonicalizer.alphaReorderQuery("") == ''
    assert surt.IAURLCanonicalizer.alphaReorderQuery("a") == 'a'
    assert surt.IAURLCanonicalizer.alphaReorderQuery("ab") == 'ab'
    assert surt.IAURLCanonicalizer.alphaReorderQuery("a=1") == 'a=1'
    assert surt.IAURLCanonicalizer.alphaReorderQuery("ab=1") == 'ab=1'
    assert surt.IAURLCanonicalizer.alphaReorderQuery("a=1&") == '&a=1'
    assert surt.IAURLCanonicalizer.alphaReorderQuery("a=1&b=1") == 'a=1&b=1'
    assert surt.IAURLCanonicalizer.alphaReorderQuery("b=1&a=1") == 'a=1&b=1'
    assert surt.IAURLCanonicalizer.alphaReorderQuery("a=a&a=a") == 'a=a&a=a'
    assert surt.IAURLCanonicalizer.alphaReorderQuery("a=b&a=a") == 'a=a&a=b'
    assert surt.IAURLCanonicalizer.alphaReorderQuery("b=b&a=b&b=a&a=a") == 'a=a&a=b&b=a&b=b'

def test_massageHost():
    # These tests are from IAURLCanonicalizerTest.java
    assert surt.IAURLCanonicalizer.massageHost("foo.com") == 'foo.com'
    assert surt.IAURLCanonicalizer.massageHost("www.foo.com") == 'foo.com'
    assert surt.IAURLCanonicalizer.massageHost("www12.foo.com") == 'foo.com'

    assert surt.IAURLCanonicalizer.massageHost("www2foo.com") == 'www2foo.com'
    assert surt.IAURLCanonicalizer.massageHost("www2.www2foo.com") == 'www2foo.com'

def test_getDefaultPort():
    # These tests are from IAURLCanonicalizerTest.java
    assert surt.IAURLCanonicalizer.getDefaultPort("foo") == 0
    assert surt.IAURLCanonicalizer.getDefaultPort("http") == 80
    assert surt.IAURLCanonicalizer.getDefaultPort("https") == 443

def test_stripPathSessionID():
    # These tests are from IAURLCanonicalizerTest.java
    # Check ASP_SESSIONID2:
    assert surt.URLRegexTransformer.stripPathSessionID("/(S(4hqa0555fwsecu455xqckv45))/mileg.aspx") == '/mileg.aspx'

    # Check ASP_SESSIONID2 (again):
    assert surt.URLRegexTransformer.stripPathSessionID("/(4hqa0555fwsecu455xqckv45)/mileg.aspx") == '/mileg.aspx'

    # Check ASP_SESSIONID3:
    assert surt.URLRegexTransformer.stripPathSessionID("/(a(4hqa0555fwsecu455xqckv45)S(4hqa0555fwsecu455xqckv45)f(4hqa0555fwsecu455xqckv45))/mileg.aspx?page=sessionschedules") == '/mileg.aspx?page=sessionschedules'

    # '@' in path:
    assert surt.URLRegexTransformer.stripPathSessionID("/photos/36050182@N05/") == '/photos/36050182@N05/'


def test_stripQuerySessionID():
    #base = "http://www.archive.org/index.html"
    base = ""
    str32id = "0123456789abcdefghijklemopqrstuv"
    url = base + "?jsessionid=" + str32id
    assert surt.URLRegexTransformer.stripQuerySessionID(url) == '?'

    # Test that we don't strip if not 32 chars only.
    url = base + "?jsessionid=" + str32id + '0'
    assert surt.URLRegexTransformer.stripQuerySessionID(url) == '?jsessionid=0123456789abcdefghijklemopqrstuv0'

    # Test what happens when followed by another key/value pair.
    url = base + "?jsessionid=" + str32id + "&x=y"
    assert surt.URLRegexTransformer.stripQuerySessionID(url) == '?x=y'

    # Test what happens when followed by another key/value pair and
    # prefixed by a key/value pair.
    url = base + "?one=two&jsessionid=" + str32id + "&x=y"
    assert surt.URLRegexTransformer.stripQuerySessionID(url) == '?one=two&x=y'

    # Test what happens when prefixed by a key/value pair.
    url = base + "?one=two&jsessionid=" + str32id
    assert surt.URLRegexTransformer.stripQuerySessionID(url) == '?one=two&'

    # Test aspsession.
    url = base + "?aspsessionidABCDEFGH=" + "ABCDEFGHIJKLMNOPQRSTUVWX" + "&x=y"
    assert surt.URLRegexTransformer.stripQuerySessionID(url) == '?x=y'

    # Test archive phpsession.
    url = base + "?phpsessid=" + str32id + "&x=y"
    assert surt.URLRegexTransformer.stripQuerySessionID(url) == '?x=y'

    # With prefix too.
    url = base + "?one=two&phpsessid=" + str32id + "&x=y"
    assert surt.URLRegexTransformer.stripQuerySessionID(url) == '?one=two&x=y'

    # With only prefix
    url = base + "?one=two&phpsessid=" + str32id
    assert surt.URLRegexTransformer.stripQuerySessionID(url) == '?one=two&'

    # Test sid.
    url = base + "?" + "sid=9682993c8daa2c5497996114facdc805" + "&x=y";
    assert surt.URLRegexTransformer.stripQuerySessionID(url) == '?x=y'

    # Igor test.
    url = base + "?" + "sid=9682993c8daa2c5497996114facdc805" + "&" + "jsessionid=" + str32id
    assert surt.URLRegexTransformer.stripQuerySessionID(url) == '?'

    url = "?CFID=1169580&CFTOKEN=48630702&dtstamp=22%2F08%2F2006%7C06%3A58%3A11"
    assert surt.URLRegexTransformer.stripQuerySessionID(url) == '?dtstamp=22%2F08%2F2006%7C06%3A58%3A11'

    url = "?CFID=12412453&CFTOKEN=15501799&dt=19_08_2006_22_39_28"
    assert surt.URLRegexTransformer.stripQuerySessionID(url) == '?dt=19_08_2006_22_39_28'

    url = "?CFID=14475712&CFTOKEN=2D89F5AF-3048-2957-DA4EE4B6B13661AB&r=468710288378&m=forgotten"
    assert surt.URLRegexTransformer.stripQuerySessionID(url) == '?r=468710288378&m=forgotten'

    url = "?CFID=16603925&CFTOKEN=2AE13EEE-3048-85B0-56CEDAAB0ACA44B8"
    assert surt.URLRegexTransformer.stripQuerySessionID(url) == '?'

    url = "?CFID=4308017&CFTOKEN=63914124&requestID=200608200458360%2E39414378"
    assert surt.URLRegexTransformer.stripQuerySessionID(url) == '?requestID=200608200458360%2E39414378'

def test_hostToSURT():
    assert surt.URLRegexTransformer.hostToSURT("www.archive.org") == 'org,archive,www'


def test_surt():
    # These tests are from WaybackURLKeyMakerTest.java

    assert surt.surt(None) == '-'
    assert surt.surt('') == '-'
    assert surt.surt("filedesc:foo.arc.gz") == 'filedesc:foo.arc.gz'
    assert surt.surt("filedesc:/foo.arc.gz") == 'filedesc:/foo.arc.gz'
    assert surt.surt("filedesc://foo.arc.gz") == 'filedesc://foo.arc.gz'
    assert surt.surt("warcinfo:foo.warc.gz") == 'warcinfo:foo.warc.gz'
    assert surt.surt("dns:alexa.com") == 'com,alexa)'
    assert surt.surt("dns:archive.org") == 'org,archive)'

    assert surt.surt("http://www.archive.org/") == 'org,archive)/'
    assert surt.surt("http://archive.org/") == 'org,archive)/'
    assert surt.surt("http://archive.org/goo/") == 'org,archive)/goo'
    assert surt.surt("http://archive.org/goo/?") == 'org,archive)/goo'
    assert surt.surt("http://archive.org/goo/?b&a") == 'org,archive)/goo?a&b'
    assert surt.surt("http://archive.org/goo/?a=2&b&a=1") == 'org,archive)/goo?a=1&a=2&b'

    # trailing comma mode
    assert surt.surt("http://archive.org/goo/?a=2&b&a=1", trailing_comma=True) == 'org,archive,)/goo?a=1&a=2&b'
    assert surt.surt("dns:archive.org", trailing_comma=True) == 'org,archive,)'
    assert surt.surt("warcinfo:foo.warc.gz", trailing_comma=True) == 'warcinfo:foo.warc.gz'

    # PHP session id:
    assert surt.surt("http://archive.org/index.php?PHPSESSID=0123456789abcdefghijklemopqrstuv&action=profile;u=4221") == 'org,archive)/index.php?action=profile;u=4221'

    # WHOIS url:
    assert surt.surt("whois://whois.isoc.org.il/shaveh.co.il") == 'whois://whois.isoc.org.il/shaveh.co.il'

    # Yahoo web bug. See https://github.com/internetarchive/surt/issues/1
    assert surt.surt('http://visit.webhosting.yahoo.com/visit.gif?&r=http%3A//web.archive.org/web/20090517140029/http%3A//anthonystewarthead.electric-chi.com/&b=Netscape%205.0%20%28Windows%3B%20en-US%29&s=1366x768&o=Win32&c=24&j=true&v=1.2') == 'com,yahoo,webhosting,visit)/visit.gif?&b=netscape%205.0%20(windows;%20en-us)&c=24&j=true&o=win32&r=http://web.archive.org/web/20090517140029/http://anthonystewarthead.electric-chi.com/&s=1366x768&v=1.2'

    # Simple customization:
    assert surt.surt("http://www.example.com/", canonicalizer=lambda x, **opts: x) == 'com,example,www)/'
    assert surt.surt("mailto:foo@example.com") == 'mailto:foo@example.com'
    assert surt.surt("http://www.example.com/", with_scheme=True) == 'http://(com,example)/'
    assert surt.surt("http://www.example.com/", with_scheme=True, host_massage=True) == 'http://(com,example)/'
    assert surt.surt("http://www.example.com/", with_scheme=False) == 'com,example)/'
    assert surt.surt("http://www.example.com/", with_scheme=True, trailing_comma=True) == 'http://(com,example,)/'
    assert surt.surt("https://www.example.com/", with_scheme=True, trailing_comma=True) == 'https://(com,example,)/'
    assert surt.surt("ftp://www.example.com/", with_scheme=True, trailing_comma=True) == 'ftp://(com,example,)/'
    assert surt.surt("http://www.example.com/", with_scheme=True, host_massage=False) == 'http://(com,example,www)/'
    assert surt.surt("http://www.example.com/", with_scheme=False, host_massage=False) == 'com,example,www)/'
    assert surt.surt("http://www.example.com/", with_scheme=True, trailing_comma=True, host_massage=False) == 'http://(com,example,www,)/'
    assert surt.surt("https://www.example.com/", with_scheme=True, trailing_comma=True, host_massage=False) == 'https://(com,example,www,)/'
    assert surt.surt("ftp://www.example.com/", with_scheme=True, trailing_comma=True, host_massage=False) == 'ftp://(com,example,www,)/'

