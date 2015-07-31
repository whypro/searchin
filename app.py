# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from lxml import etree
from StringIO import StringIO
from urlparse import urljoin

import tornado.ioloop
import tornado.web
import tornado.httpclient
import tornado.httpserver


class Paper(object):

    def __init__(self):
        pass


class MainHandler(tornado.web.RequestHandler):
    @tornado.web.authenticated
    def get(self):
        name = self.current_user
        self.render('index.html', name=name)

    def get_current_user(self):
        return self.get_secure_cookie('user')


class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        self.set_secure_cookie('user', self.get_argument('name'))
        self.redirect('/')

class AsyncHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.write('async')
        self.finish()


class SearchHandler(tornado.web.RequestHandler):

    page = 0

    def get(self):
        self.render('search.html')

    @tornado.web.asynchronous
    def post(self):
        self.papers = []
        key = self.get_argument('key')
        page = self.get_argument('page')
        self.max_page = int(page)
        http = tornado.httpclient.AsyncHTTPClient()
        url_template = 'http://xueshu.baidu.com/s?wd={key}&rsv_bp=0&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8'
        http.fetch(
            url_template.format(key=key),
            callback=self._on_response
        )


    def _on_response(self, response):
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(response.body), parser)
        items = tree.xpath('//div[@class="result xpath-log"]')
        

        for item in items:
            # 标题 和 URL
            _title = item.xpath('div[@class="sc_content"]/h3/a')
            if not _title:
                continue
            title = _title[0].xpath('string(.)')
            url = item.xpath('div[@class="sc_content"]/h3/a/@href')[0]

            authors = item.xpath('div[@class="sc_content"]/div[@class="sc_info"]/span[1]/a/text()')
            journal = item.xpath('div[@class="sc_content"]/div[@class="sc_info"]/a[1]/@title')[0].strip('《').strip('》')
            year = item.xpath('div[@class="sc_content"]/div[@class="sc_info"]/span[2]/text()')[0]
            key_words = item.xpath('div[@class="sc_content"]/div[@class="c_abstract"]/p/span/a/text()')
            cite_num = item.xpath('div[@class="sc_ext"]/div[@class="sc_cite"]//span[@class="sc_cite_num c-gray"]/text()')[0]

            paper = Paper()
            paper.title = title
            paper.url = url
            paper.authors = authors
            paper.journal = journal
            paper.year = year
            paper.key_words = key_words
            paper.cite_num = cite_num

            self.papers.append(paper)

            # print 'title', title
            # print 'url', url
            # print 'authors', authors
            # print 'journal', journal
            # print 'year', year
            # print 'key_words', key_words

        if self.page <= self.max_page:
            next_page = tree.xpath('//p[@id="page"]/a[last()]/@href')[0]
            url = urljoin(response.effective_url, next_page)
            http = tornado.httpclient.AsyncHTTPClient()
            http.fetch(url, callback=self._on_response)
            self.page += 1
        else:
            self.render('search_result.html', papers=self.papers)
        # self.finish()

if __name__ == '__main__':
    settings = {
        'cookie_secret': "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
        'login_url': '/login',
        # 'xsrf_cookies': True,
        'static_path': os.path.join(os.path.dirname(__file__), 'static'),
        'debug': True,
    }

    app = tornado.web.Application([
        (r'/', MainHandler), 
        (r'/login', LoginHandler),
        (r'/async', AsyncHandler),
        (r'/search', SearchHandler),
    ], **settings)

    http_server = tornado.httpserver.HTTPServer(app)
    port = int(os.environ.get("PORT", 5000))
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()
