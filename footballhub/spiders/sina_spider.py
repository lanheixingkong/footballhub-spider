# -*- coding: utf-8 -*-
from scrapy.http import Request
from scrapy.spiders import Spider
from scrapy.http.headers import Headers
import os
import sys
from hashlib import md5
from footballhub.items import ArticleItem
from urllib import urlencode
import json


class SinaSpider(Spider):
    name = "sina"

    RENDER_HTML_URL = "http://222.85.139.246:18050/render.html"

    def setencoding(self):
        # print "--------ori:"+sys.getdefaultencoding()
        reload(sys)                         # 2
        sys.setdefaultencoding('utf-8')
        # print "--------new:"+sys.getdefaultencoding()

    def start_requests(self):
        self.setencoding()
        url = "http://roll.sports.sina.com.cn/s/channel.php?ch=02#col=65,66&spec=&type=&ch=02&k=&offset_page=0&offset_num=0&num=60&asc=&page=1"
        body = json.dumps({"url": url, "wait": 5,'images':0,'allowed_content_types':'text/html; charset=utf-8'})
        headers = Headers({'Content-Type': 'application/json'})
        yield Request(self.RENDER_HTML_URL, self.parse, method="POST",
                                 body=body, headers=headers)
        pass

    def parse(self, response):
        # follow links to author pages
        for a in response.css(".c_tit a"):
            title = a.xpath("text()").extract_first()

            if not title.startswith("图文") and not title.startswith("视频"):
                href = a.xpath("@href").extract_first()
                # href = "http://sports.sina.com.cn/g/pl/2017-05-17/doc-ifyfeivp5814230.shtml"
                yield Request(response.urljoin(href),
                             callback=self.parse_detail)
            else:
                pass
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


        title = extract_with_css('.article-a__title::text')
        timestr = extract_with_css(".article-a__time::text")
        posttime = timestr.replace("年", "-").replace("月", "-").replace("日", " ") + ":00"
        sourceUrl = extract_with_css(".article-a__source a::attr(href)")
        sourceName = extract_with_css(".article-a__source a::text")
        content = ''.join(map(lambda str: str.strip().decode('utf-8'), response.xpath("//div[@id='artibody']/figure|//div[@id='artibody']/p").extract()))
        contentText = ''.join(map(lambda str: str.strip().decode('utf-8'), response.xpath("//div[@id='artibody']/p/text()").extract()))

        item = ArticleItem()
        item['title'] = title
        item['posttime'] = posttime
        item['sourceUrl'] = sourceUrl
        item['sourceName'] = sourceName
        item['content'] = content
        item['contentText'] = contentText
        item['crawlSite'] = 'sina'
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
