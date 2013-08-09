Sort-friendly URI Reordering Transform (SURT) python package.

Usage:

    >>> from surt import surt
    >>> surt("http://archive.org/goo/?a=2&b&a=1")
    'org,archive)/goo?a=1&a=2&b'

Installation:

    pip install surt

Or install the dev version from git:

    pip install git+git://github.com/rajbot/surt#egg=surt


More information about SURTs:
http://crawler.archive.org/articles/user_manual/glossary.html#surt

This is mostly a python port of the archive-commons org.archive.url package.
The original java version of the org.archive.url package is here:
http://archive-access.svn.sourceforge.net/viewvc/archive-access/trunk/archive-access/projects/archive-commons/src/main/java/org/archive/url/

This module depends on the `tldextract` module to query the Public Suffix
List. `tldextract` can be installed via `pip`

[![Build Status](https://secure.travis-ci.org/rajbot/surt.png?branch=master)](http://travis-ci.org/rajbot/surt)
