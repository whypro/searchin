# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from lxml import etree
from StringIO import StringIO
from urlparse import urljoin
from collections import defaultdict
import json

import tornado.web
import tornado.httpclient
import tornado.gen

from ..models import Paper


class SearchHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):

        self.page = defaultdict(int)
        self.papers = []
        self.max_page = 0

        tornado.web.RequestHandler.__init__(self, application, request, **kwargs)

    def get(self):
        self.render('search.html')

    @tornado.gen.coroutine
    def post(self):
        self.papers = []
        key = self.get_argument('key')
        page = self.get_argument('page')
        self.max_page = int(page)
        http = tornado.httpclient.AsyncHTTPClient()
        url_template = 'http://xueshu.baidu.com/s?wd={key}&rsv_bp=0&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8'
        # response = yield tornado.gen.Task(http.fetch, url_template.format(key=key))
        response = yield http.fetch(url_template.format(key=key))
        self.parse_html(response)

        # 将搜索关键词插入数据库
        self.application.db.queries.update_one({'key': key}, {'$inc': {'count': 1}}, upsert=True)

        papers_cursor = self.load_papers(key)
        papers_dict = [p for p in papers_cursor]
        result_dict = {'key': key, 'count': len(papers_dict), 'papers': papers_dict}
        result_json = json.dumps(result_dict, ensure_ascii=False, encoding='utf-8')
        self.set_header('Content-Type', 'application/javascript; charset=utf-8')
        self.write(result_json)
        self.finish()

        # papers = [Paper(**p) for p in papers_dict]
        # papers_json = tornado.escape.json_encode('{"哈哈": "你好"}')
        # self.write(papers_json)
        # self.finish()
        # self.render('search_result.html', papers=papers)

    @tornado.gen.coroutine
    def parse_html(self, response):
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(response.body), parser)
        areas = tree.xpath('//div[@class="leftnav_list leftnav_list_show"]/div/a')
        for area in areas:
            title = area.xpath('@title')[0].strip()
            href = area.xpath('@href')[0]
            http = tornado.httpclient.AsyncHTTPClient()
            response = yield http.fetch(urljoin('http://xueshu.baidu.com', href))
            self.parse_papers(response, title)

    @tornado.gen.coroutine
    def parse_papers(self, response, area):
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
            _year = item.xpath('div[@class="sc_content"]/div[@class="sc_info"]/span[@class="sc_time"]/text()')
            year = _year[0] if _year else ''
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
            paper.click_num = 0
            paper.area = area

            self.papers.append(paper)

            # print 'title', title
            # print 'url', url
            # print 'authors', authors
            # print 'journal', journal
            # print 'year', year
            # print 'key_words', key_words

        if self.page[area] <= self.max_page:
            self.page[area] += 1
            next_page = tree.xpath('//p[@id="page"]/a[last()]/@href')[0]
            url = urljoin(response.effective_url, next_page)
            http = tornado.httpclient.AsyncHTTPClient()
            response = yield http.fetch(url)
            self.parse_papers(response, area)
        else:
            self.save_papers(self.papers)
            print area, self.page[area]

    def save_papers(self, papers):
        for paper in papers:
            self.application.db.papers.update_one({'url': paper.url}, {'$set': paper.__dict__}, upsert=True)

    def load_papers(self, key):
        papers = self.application.db.papers.find({'title': {'$regex': key}}, {'_id': False})
        print papers.count()
        return papers

