Sort-friendly URI Reordering Transform (SURT) python package.

Usage:
    >>> from surt import surt
    >>> surt("http://archive.org/goo/?a=2&b&a=1")
    'org,archive)/goo?a=1&a=2&b'

More information about SURTs:
http://crawler.archive.org/articles/user_manual/glossary.html#surt

This is mostly a python port of the archive-commons org.archive.url package.
The original java version of the org.archive.url package is here:
http://archive-access.svn.sourceforge.net/viewvc/archive-access/trunk/archive-access/projects/archive-commons/src/main/java/org/archive/url/

I originally thought I could generate the SURT form of a url in 3 lines
of python. That turned into 5 lines, and then 4 more lines for query
re-ordering, and the results still didn't match the results from the
IA Webcrawler. I ended up having to port a lot of java code, much of
it verbatim, avoiding methods in python's standard library that
produced slightly different results. Had I known this before starting,
I would have never written this module.

This module depends on the `tldextract` module to query the Public Suffix
List. `tldextract` can be installed via `pip`
