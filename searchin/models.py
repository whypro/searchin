# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class Paper(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __str__(self):
        return str(self.__dict__)


class Book(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __str__(self):
        return str(self.__dict__)
