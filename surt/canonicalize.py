#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A script for canonicalize (non-surt currently) a stream of urls from stdin

from surt import surt

import sys

for line in sys.stdin:
  url = line.rstrip()

  print surt(url, surtMode=False, includeScheme=False)

