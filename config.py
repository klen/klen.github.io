# coding: utf-8
import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '_plugins'))

# Pelican settings (look at http://docs.getpelican.com/en/3.4.0/settings.html)

AUTHOR = 'Kirill Klenov'
DEFAULT_DATE = 'fs'
DEFAULT_LANG = 'ru'
DISQUS_SITENAME = 'klengithubcom'
GITHUB_URL = 'https://github.com/klen'
PLUGINS = ['neighbors', 'multi_part', 'youtube']
PYGMENTS_RST_OPTIONS = {'linenos': 'table'}
RELATIVE_URLS = True
SITENAME = 'klen.github.io'
SITEURL = 'http://klen.github.io'
STATIC_PATHS = ['static']
THEME = '_theme'
TIMEZONE = 'Europe/Moscow'

# Other settings
FEED_TITLE = 'klen.github.io - all posts'
FEED_URL = 'http://feeds.feedburner.com/klengihubcom'
MYOPENID_IDENTIFICATOR = 'horneds'
YANDEX_VERIFICATION = '6a6ba8237dcc1d3e'
GOOGLE_VERIFICATION = 'PhpguXH83A1Tir-QHZRoJYOO5FF5Tfwmqqo85NFtdSI'
GITHUB_IDENTIFICATOR = 'http://github.com/klen'
