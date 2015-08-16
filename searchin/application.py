# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from pymongo import MongoClient

import tornado.web

from .handlers import SearchHandler


class Application(tornado.web.Application):
    def __init__(self):

        handlers = [
            (r'/search', SearchHandler),
        ]

        settings = {
            'cookie_secret': "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            'login_url': '/login',
            # 'xsrf_cookies': True,
            'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
            'static_path': os.path.join(os.path.dirname(__file__), 'static'),
            'debug': True,
            'db_host': '192.168.7.103',
            'db_port': 27017,
            'db_name': 'searchin'
        }

        client = MongoClient(host=settings['db_host'], port=settings['db_port'])
        self.db = client[settings['db_name']]

        tornado.web.Application.__init__(self, handlers, **settings)

