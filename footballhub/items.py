# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FootballhubItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ArticleItem(scrapy.Item):

    title = scrapy.Field()
    posttime = scrapy.Field()
    sourceUrl = scrapy.Field()
    sourceName = scrapy.Field()
    content = scrapy.Field()
    contentText = scrapy.Field()
    link = scrapy.Field()
    linkmd5id = scrapy.Field()
    crawlSite = scrapy.Field()
