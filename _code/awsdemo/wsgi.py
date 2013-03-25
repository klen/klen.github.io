#!/usr/bin/env python
#-*- coding: utf-8 -*-

from os import environ

from django.core.handlers.wsgi import WSGIHandler


environ['DJANGO_SETTINGS_MODULE'] = environ.get(
    'DJANGO_SETTINGS_MODULE', 'settings')

application = WSGIHandler()
