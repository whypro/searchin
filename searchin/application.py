# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

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
        }

        tornado.web.Application.__init__(self, handlers, **settings)

