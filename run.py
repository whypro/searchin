# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

import tornado.httpserver
import tornado.ioloop

from searchin.application import Application

if __name__ == '__main__':
    app = Application()
    server = tornado.httpserver.HTTPServer(app)
    port = int(os.environ.get("PORT", 5000))
    server.listen(port)
    tornado.ioloop.IOLoop.instance().start()
