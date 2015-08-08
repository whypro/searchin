# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import tornado.httpserver
import tornado.ioloop

from searchin.application import Application

if __name__ == '__main__':
    app = Application()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(5000)
    tornado.ioloop.IOLoop.instance().start()
