#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A script for canonicalize (non-surt currently) a stream of urls from stdin

import sys
import surt


encountered_error = False

for line in sys.stdin:
    url = line.rstrip()

    try:
        print surt.surt(url, surtMode=False, includeScheme=False)
    except:
        sys.stderr.write("Error: Invalid url %s\n" % url)
	encountered_error = True

if encountered_error:
    exit(1)

exit(0)
