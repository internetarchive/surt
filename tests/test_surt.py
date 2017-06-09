# -*- coding: utf-8 -*-

from __future__ import absolute_import

import surt
from surt._surtformat import hostToSURT

import pytest
import itertools

@pytest.fixture(params=itertools.product(
    [('_', None), ('with_scheme', False), ('with_scheme', True)],
    [('_', None), ('trailing_comma', False), ('trailing_comma', True)],
    [('_', None), ('reverse_ipaddr', True), ('reverse_ipaddr', False)]
))
def format_options(request):
    o = dict(request.param)
    o.pop('_', None)
    return o

@pytest.mark.parametrize("host_in,host_out", [
    (b"www.archive.org", [b"org,archive,www", b"org,archive,www"]),
    (b"123.123.net", [b"net,123,123", b"net,123,123"]),
    (b"100.100.100.100.org", [b"org,100,100,100,100", b"org,100,100,100,100"]),
    (b"123.45.167.89", [b"89,167,45,123", b"123.45.167.89"]),
    (b"10.162.1024.3", [b"3,1024,162,10", b"3,1024,162,10"]),
    # any four period-delimited 1-3 digit integers are interpreted as IP address, currently
    (b"990.991.992.993", [b"993,992,991,990", b"990.991.992.993"])
])
def test_hostToSURT(host_in, host_out):
    h = hostToSURT

    assert h(host_in) == host_out[0]
    assert h(host_in, reverse_ipaddr=True) == host_out[0]
    assert h(host_in, reverse_ipaddr=False) == host_out[1]

def test_surt_no_url():
    # TODO: we may change this to None
    assert surt.surt(None) == '-'
    # TODO: we may change this to ''
    assert surt.surt('') == '-'

def test_surt_dns(format_options):
    """dns: URI remains identical regardless of options."""
    assert surt.surt("dns:archive.org", **format_options) == "dns:archive.org"
    assert surt.surt("dns:alexa.com", **format_options) == 'dns:alexa.com'

def test_surt_warcinfo(format_options):
    """warcinfo: URI remains identical regardless of options."""
    assert surt.surt("warcinfo:foo.warc.gz", **format_options) == 'warcinfo:foo.warc.gz'

def test_surt_mailto(format_options):
    """mailto URI remains identical regardless of options."""
    assert surt.surt("mailto:foo@example.com", **format_options) == 'mailto:foo@example.com'

def test_surt_filedesc(format_options):
    """filedesc URI remains identical regardless of options."""
    assert surt.surt("filedesc:foo.arc.gz", **format_options) == 'filedesc:foo.arc.gz'
    assert surt.surt("filedesc:/foo.arc.gz", **format_options) == 'filedesc:/foo.arc.gz'
    assert surt.surt("filedesc://foo.arc.gz", **format_options) == 'filedesc://foo.arc.gz'

def expected_surt(options, scheme, host, path_query, trailing_comma_values=['', ',']):
    return ''.join([
        ('', scheme + '://(')[options.get('with_scheme', False)],
        host,
        trailing_comma_values[options.get('trailing_comma', False)],
        ')',
        path_query
        ])

def test_surt_whois(format_options):
    """WHOIS URL."""
    expected = expected_surt(format_options, 'whois', 'il,org,isoc,whois', '/shaveh.co.il')
    assert surt.surt("whois://whois.isoc.org.il/shaveh.co.il", **format_options) == expected

def test_surt_http(format_options):
    def s(url, **canon_options):
        options = dict(format_options, **canon_options) if canon_options else format_options
        return surt.surt(url, **options)
    def e(*comps):
        return expected_surt(format_options, *comps)

    assert s("http://www.archive.org/") == e('http', 'org,archive', '/')
    assert s("http://www.archive.org/", host_massage=False) == e('http', 'org,archive,www', '/')

    assert s("http://archive.org/") == e('http', 'org,archive', '/')
    assert s("http://archive.org/goo/") == e('http', 'org,archive', '/goo')
    assert s("http://archive.org/goo/?") == e('http', 'org,archive', '/goo')
    assert s("http://archive.org/goo/?b&a") == e('http', 'org,archive', '/goo?a&b')
    assert s("http://archive.org/goo/?a=2&b&a=1") == e('http', 'org,archive', '/goo?a=1&a=2&b')

    assert s("https://www.example.com/") == e('https', 'com,example', '/')

    # PHP session id:
    assert s("http://archive.org/index.php?PHPSESSID=0123456789abcdefghijklemopqrstuv&action=profile;u=4221") \
        == e('http', 'org,archive', '/index.php?action=profile;u=4221')

def test_surt_ftp(format_options):
    def s(url, **canon_options):
        options = dict(format_options, **canon_options) if canon_options else format_options
        return surt.surt(url, **options)
    def e(*comps):
        return expected_surt(format_options, *comps)

    assert s("ftp://www.example.com/") == e('ftp', 'com,example', '/')
    assert s("ftp://www.example.com/", host_massage=False) == e('ftp', 'com,example,www', '/')

def test_surt():
    # Yahoo web bug. See https://github.com/internetarchive/surt/issues/1
    assert surt.surt('http://visit.webhosting.yahoo.com/visit.gif?&r=http%3A//web.archive.org/web/20090517140029/http%3A//anthonystewarthead.electric-chi.com/&b=Netscape%205.0%20%28Windows%3B%20en-US%29&s=1366x768&o=Win32&c=24&j=true&v=1.2') == 'com,yahoo,webhosting,visit)/visit.gif?&b=netscape%205.0%20(windows;%20en-us)&c=24&j=true&o=win32&r=http://web.archive.org/web/20090517140029/http://anthonystewarthead.electric-chi.com/&s=1366x768&v=1.2'

    # Simple customization:
    assert surt.surt("http://www.example.com/", canonicalizer=lambda x, **opts: x) == 'com,example,www)/'


@pytest.mark.parametrize("url,out", [
    ("http://192.168.1.254/info/", ('http', ['192.168.1.254', '254,1,168,192'], '/info')),
])
def test_surt_ipaddress(url, format_options, out):
    expected = expected_surt(format_options,
                             out[0],
                             out[1][format_options.get('reverse_ipaddr', True)],
                             out[2],
                             trailing_comma_values=['', ''])
    assert surt.surt(url, **format_options) == expected
    assert surt.surt(url, host_massage=False, **format_options) == expected

@pytest.mark.parametrize("url,out", [
    # this illustrates a bug in canonicalization of query part.
    # expected to fail until fixed.
    pytest.param(
        "http://exmaple.com/script?type=a+b+%26+c&grape=wine",
        "com,example)/script?grape=wine&type=a+b+%26+c", marks=pytest.mark.xfail)
])
def test_surt_query(url, out):
    assert surt.surt(url) == out

def test_surt_override_canonicalizer():
    """Use alternative canonicalizer. With GoogleURLCaonicalizer only, session-ID
    parameters are not removed.
    """
    url = "http://example.com/article?aid=0020345&PHPSESSID=0123456789abcdefghijklemopqrstuv"
    s = surt.surt(url, canonicalizer=surt.GoogleURLCanonicalizer)
    assert s == "com,example)/article?aid=0020345&PHPSESSID=0123456789abcdefghijklemopqrstuv"

    # non-practical caonicalizer that makes hostname all uppercase
    def upcase_host(hurl, **options):
        hurl.host = hurl.host.upper()
        return hurl

    # combine it with GoogleURLCanonicalizer
    s = surt.surt(url, canonicalizer=(surt.GoogleURLCanonicalizer, upcase_host))
    assert s == "COM,EXAMPLE)/article?aid=0020345&PHPSESSID=0123456789abcdefghijklemopqrstuv"

@pytest.mark.parametrize("burl", [
        b'http://example.com/'
        ])
def test_surt_return_type(burl):
    """surt.surt() returns the same type of string object (i.e. returns unicode
    string for unicode string input, and byets for bytes)

    Note this behavior may change in the future versions. This test is for
    testing compatibility until that happens.
    """
    assert isinstance(burl, bytes)

    b = surt.surt(burl)
    assert type(b) is type(burl)

    uurl = burl.decode('ascii')
    u = surt.surt(uurl)
    assert type(u) is type(uurl)
