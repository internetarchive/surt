# -*- coding: utf-8 -*-

from surt import handyurl
import pytest

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

    assert handyurl.parse("mailto:bot@archive.org").scheme == b'mailto'
    assert handyurl.parse("mailto:bot@archive.org").geturl() == 'mailto:bot@archive.org'

def test_getPublicSuffix():
    # These tests are based off the ones found in HandyURLTest.java
    assert handyurl(host='www.fool.com').getPublicSuffix() == b'fool.com'
    assert handyurl(host='www.amazon.co.uk').getPublicSuffix() == b'amazon.co.uk'
    assert handyurl(host='www.images.amazon.co.uk').getPublicSuffix() == b'amazon.co.uk'
    assert handyurl(host='funky-images.fancy.co.jp').getPublicSuffix() == b'fancy.co.jp'

def test_getPublicPrefix():
    # These tests are based off the ones found in HandyURLTest.java
    assert handyurl(host='www.fool.com').getPublicPrefix() == 'www'
    assert handyurl(host='www.amazon.co.uk').getPublicPrefix() == 'www'
    assert handyurl(host='www.images.amazon.co.uk').getPublicPrefix() == 'www.images'
    assert handyurl(host='funky-images.fancy.co.jp').getPublicPrefix() == 'funky-images'
