#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.
import os
import sys

sys.path.append(os.curdir)
from pelicanconf import *  # pylint: disable=unused-import

# If your site is available via HTTPS, make sure SITEURL begins with https://
SITEURL = "https://iwanttoreadmore.com"
RELATIVE_URLS = False

FEED_ALL_ATOM = "feeds/all.atom.xml"
FEED_ALL_RSS = "feeds/all.rss.xml"

DELETE_OUTPUT_DIRECTORY = True
