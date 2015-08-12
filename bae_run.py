#!/usr/bin/env python
# -*- coding:utf-8 -*-
from bae.core.wsgi import WSGIApplication
import tornado.wsgi

from searchin.application import Application

app = Application()
wsgi_app = tornado.wsgi.WSGIAdapter(app)
application = WSGIApplication(wsgi_app)

