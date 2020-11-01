#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# General website settings
AUTHOR = "Vladimir Haltakov"
SITENAME = "I Want To Read More"
SITEURL = "https://iwanttoreadmore.com"
SITEDESCRIPTION = "I Want To Read More is a tool that helps bloggers to collect feedback from their readers about what topics they want to read more about."
PATH = "content"
TIMEZONE = "Europe/Berlin"
DEFAULT_LANG = "en"
DEFAULT_DATE_FORMAT = "%d %b %Y"
SUMMARY_MAX_LENGTH = 40

# Set the theme to minimal
THEME = "themes/minimal/"

# Static pages of the website that will be generated
TEMPLATE_PAGES = {
    "pages/index.html": "index.html",
    "pages/stats.html": "stats.html",
    "pages/email/confirm_email.html": "confirm_email.html",
    "pages/email/confirm_subscription.html": "confirm_subscription.html",
    "pages/email/confirm_subscription_beta.html": "confirm_subscription_beta.html",
    "pages/user/login.html": "login.html",
    "pages/404.html": "404.html",
}

# Static paths of the website
# The _redirects file is used by Netlify to create redirect rules
STATIC_PATHS = ["images", "_redirects", "robots.txt"]

# Settings for the URLs of the blog and the articles
ARTICLE_PATHS = ["blog"]
ARTICLE_URL = "blog/{slug}/"
ARTICLE_SAVE_AS = "blog/{slug}/index.html"
INDEX_SAVE_AS = "blog.html"

# Enable the jinja2content plugin
PLUGIN_PATHS = ["plugins"]
PLUGINS = ["jinja2content"]

# Enable document-relative URLs when developing
RELATIVE_URLS = True

# Disbale unneeded blog features
ARCHIVES_SAVE_AS = ""
AUTHOR_SAVE_AS = ""
AUTHORS_SAVE_AS = ""
CATEGORY_SAVE_AS = ""
CATEGORIES_SAVE_AS = ""
TAGS_SAVE_AS = ""

# Disable all feed generation while developing
FEED_ALL_ATOM = None
FEED_ALL_RSS = None
