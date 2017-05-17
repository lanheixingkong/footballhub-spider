import scrapy
import os

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes/quotes-%s.html' % page
        if not os.path.exists("quotes"):
            os.makedirs("quotes")
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
