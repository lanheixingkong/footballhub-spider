# -*- coding: utf-8 -*-
import scrapy
import os
import sys
from hashlib import md5
from footballhub.items import ArticleItem
from urllib import urlencode


class Zhibo8Spider(scrapy.Spider):
    name = "zhibo8"


    def setencoding(self):
        # print "--------ori:"+sys.getdefaultencoding()
        reload(sys)                         # 2
        sys.setdefaultencoding('utf-8')
        # print "--------new:"+sys.getdefaultencoding()

    def start_requests(self):
        self.setencoding()

        url = 'https://news.zhibo8.cc/zuqiu/more.htm'
        label = getattr(self, 'label', None)
        print "-------------label:%s" % label
        if label is not None:
            url = url + '?' + urlencode({'label':label})
        print "-------------url:%s" % url
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        idx = 0
        # follow links to author pages
        for href in response.css(".articleTitle a::attr(href)").extract():
            detailurl = "https:" + href
            yield scrapy.Request(response.urljoin(detailurl),
                             callback=self.parse_detail)
            idx = idx + 1
            if idx >= 5:
                break
            # break

        # follow pagination links
        #next_page = response.css('li.next a::attr(href)').extract_first()
        #if next_page is not None:
        #
        #    yield scrapy.Request(next_page, callback=self.parse)

    # def parse(self, response):
    #     l = ItemLoader(item=Product(), response=response)
    #     l.add_xpath('name', '//div[@class="product_name"]')
    #     l.add_xpath('name', '//div[@class="product_title"]')
    #     l.add_xpath('price', '//p[@id="price"]')
    #     l.add_css('stock', 'p#stock]')
    #     l.add_value('last_updated', 'today') # you can also use literal values
    #     return l.load_item()

    def parse_detail(self, response):
        # def extract_with_css(title, query):
            #return title + ":" +response.css(query).extract_first().strip().decode('utf-8') + "\n"

        def extract_with_css(query):
            str = response.css(query).extract_first()
            if str is not None:
                return str.strip().decode('utf-8')
            else:
                return ""


        title = extract_with_css('.title h1::text')
        posttime = extract_with_css("span[ms-controller='title_controller']::text")
        sourceUrl = extract_with_css("span[ms-controller='title_controller'] a::attr(href)")
        sourceName = extract_with_css("span[ms-controller='title_controller'] a::text")
        content = ''.join(map(lambda str: str.strip().decode('utf-8'), response.xpath("//div[@id='signals']/p").extract()))
        contentText = ''.join(map(lambda str: str.strip().decode('utf-8'), response.xpath("//div[@id='signals']/p/text()").extract()))

        item = ArticleItem()
        item['title'] = title
        item['posttime'] = posttime
        item['sourceUrl'] = sourceUrl
        item['sourceName'] = sourceName
        item['content'] = content
        item['contentText'] = contentText
        item['crawlSite'] = 'zhibo8'
        url = response.url
        item['link'] = url
        data = url + ":" + title
        linkmd5id = self._get_linkmd5id(data)
        item['linkmd5id'] = linkmd5id

        yield item

        # page = response.url.split("/")[-1]
        # filename = 'zhibo8/detail-%s' % page
        # if not os.path.exists("zhibo8"):
        #     os.makedirs("zhibo8")
        # with open(filename, 'wb') as f:
        #     f.write(extract_with_css('title', '.title h1::text'))
        #     f.write(extract_with_css('posttime', "span[ms-controller='title_controller']::text"))
        #     f.write(extract_with_css('sourceUrl', "span[ms-controller='title_controller'] a::attr(href)"))
        #     f.write(extract_with_css('sourceName', "span[ms-controller='title_controller'] a::text"))
        #     f.write("content:"+''.join(response.xpath("//div[@id='signals']/p").extract())+"\n")
        #     f.write("contentText:"+''.join(response.xpath("//div[@id='signals']/p/text()").extract()))
        # self.log('Saved file %s' % filename)

        # yield {
        #     'title': extract_with_css('.title h1::text'),
        #     'posttime': extract_with_css("span[ms-controller='title_controller']::text"),
        #     'sourceUrl': extract_with_css("span[ms-controller='title_controller'] a::attr(href)"),
        #     'sourceName': extract_with_css("span[ms-controller='title_controller'] a::text"),
        #     'content': response.xpath("string(//div[@id='signals'])").extract_first()
        # }


    #获取url的md5编码
    def _get_linkmd5id(self, data):
        #url进行md5处理，为避免重复采集设计
        return md5(data).hexdigest()

    #异常处理
    def _handle_error(self, failue, item, spider):
        log.err(failure)
