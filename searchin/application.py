# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from pymongo import MongoClient

import tornado.web

from .handlers import HomeHandler, PaperSearchHandler, BookSearchHandler


class Application(tornado.web.Application):
    def __init__(self):

        settings = {
            'cookie_secret': "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            'login_url': '/login',
            # 'xsrf_cookies': True,
            'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
            'static_path': os.path.join(os.path.dirname(__file__), 'static'),
            'debug': True,
            'db_host': 'localhost',
            'db_port': 27017,
            'db_name': 'searchin'
        }

        handlers = [
            (r'/', HomeHandler),
            (r'/paper/search', PaperSearchHandler),
            (r'/book/search', BookSearchHandler),
            (r'/favicon\.ico', tornado.web.StaticFileHandler, dict(path=settings['static_path']))
        ]

        self.client = MongoClient(host=settings['db_host'], port=settings['db_port'])
        self.db = self.client[settings['db_name']]

        tornado.web.Application.__init__(self, handlers, **settings)

    def __del__(self):
        self.client.close()

