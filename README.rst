Sort-friendly URI Reordering Transform (SURT) python package.

Usage:

::

    >>> from surt import surt
    >>> surt("http://archive.org/goo/?a=2&b&a=1")
    'org,archive)/goo?a=1&a=2&b'

Installation:

::

    pip install surt

Or install the dev version from git:

::

    pip install git+https://github.com/internetarchive/surt.git#egg=surt

More information about SURTs:
http://crawler.archive.org/articles/user\_manual/glossary.html#surt

This is mostly a python port of the webarchive-commons org.archive.url
package. The original java version of the org.archive.url package is
here:
https://github.com/iipc/webarchive-commons/tree/master/src/main/java/org/archive/url

This module depends on the ``tldextract`` module to query the Public
Suffix List. ``tldextract`` can be installed via ``pip``

|Build Status|

.. |Build Status| image:: https://travis-ci.org/internetarchive/surt.svg
   :target: https://travis-ci.org/internetarchive/surt
