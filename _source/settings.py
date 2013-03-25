#!/usr/bin/env python
# coding: utf-8

# Base
AUTHOR = 'Kirill Klenov'
SITENAME = 'klen.github.com'
SITEURL = SITE_URL = 'http://klen.github.com'
REVERSE_ARCHIVE_ORDER = True
TIMEZONE = 'Europe/Moscow'
PELICAN_CLASS = 'ext.KlenPelican'

FEED_URL = 'http://feeds.feedburner.com/klengihubcom'
FEED_TITLE = 'klen.github.com -- all posts'

YANDEX_VERIFICATION = '6a6ba8237dcc1d3e'
GOOGLE_VERIFICATION = 'PhpguXH83A1Tir-QHZRoJYOO5FF5Tfwmqqo85NFtdSI'
GITHUB_IDENTIFICATOR = 'http://github.com/klen'
MYOPENID_IDENTIFICATOR = 'horneds'
DISQUS_SHORTNAME = 'klengithubcom'

TAG_CLOUD_STEPS = 6
TAG_CLOUD_MAX_ITEMS = 100

CATALOG = dict(
        Books = dict(
            note = u"Лента прочитанных мной книг. Впечатления в паре предложений.",
            preview = True,
        ),

        Notes = dict(
            note = u"Ссылки и заметки о веб-технологиях.",
        ),

        Blog = dict(
            note = u"Статьи о веб-разработке.",
            tags = True,
        )
)
