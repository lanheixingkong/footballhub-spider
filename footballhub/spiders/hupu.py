# -*- coding: utf-8 -*-
import scrapy
import os
import sys
from hashlib import md5
from footballhub.items import ArticleItem
from urllib import urlencode


class HuPuSpider(scrapy.Spider):
    name = "hupu"


    def setencoding(self):
        # print "--------ori:"+sys.getdefaultencoding()
        reload(sys)                         # 2
        sys.setdefaultencoding('utf-8')
        # print "--------new:"+sys.getdefaultencoding()

    def start_requests(self):
        self.setencoding()

        url = 'https://voice.hupu.com/soccer'
        yield scrapy.Request(url, self.parse)

    def parse(self, response):

        # follow links to author pages
        for href in response.css(".list-hd a::attr(href)").extract():
            yield scrapy.Request(response.urljoin(href),
                             callback=self.parse_detail)


    def parse_detail(self, response):
        # def extract_with_css(title, query):
            #return title + ":" +response.css(query).extract_first().strip().decode('utf-8') + "\n"

        def extract_with_css(query):
            str = response.css(query).extract_first()
            if str is not None:
                return str.strip().decode('utf-8')
            else:
                return ""


        title = extract_with_css('.artical-title h1::text')
        posttime = extract_with_css("#pubtime_baidu::text")
        sourceUrl = extract_with_css(".comeFrom a::attr(href)")
        sourceName = extract_with_css(".comeFrom a::text")
        content = ''.join(map(lambda str: str.strip().decode('utf-8'), response.xpath("//div[@class='artical-content-read']/div").extract()))
        contentText = ''.join(map(lambda str: str.strip().decode('utf-8'), response.xpath("//div[@class='artical-main-content']/p/text()").extract()))

        item = ArticleItem()
        item['title'] = title
        item['posttime'] = posttime
        item['sourceUrl'] = sourceUrl
        item['sourceName'] = sourceName
        item['content'] = content
        item['contentText'] = contentText
        item['crawlSite'] = 'hupu'
        url = response.url
        item['link'] = url
        data = url + ":" + title
        linkmd5id = self._get_linkmd5id(data)
        item['linkmd5id'] = linkmd5id

        yield item


    #获取url的md5编码
    def _get_linkmd5id(self, data):
        #url进行md5处理，为避免重复采集设计
        return md5(data).hexdigest()

    #异常处理
    def _handle_error(self, failue, item, spider):
        log.err(failure)
