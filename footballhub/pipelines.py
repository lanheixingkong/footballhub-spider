# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os
import MySQLdb
from scrapy.exceptions import DropItem
import sys
sys.path.append("/root/python-space/mymodule")
import fenci


class FootballhubPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWriterPipeline(object):

    def open_spider(self, spider):
        if not os.path.exists("zhibo8"):
            os.makedirs("zhibo8")
        self.file = open('zhibo8/items.jl', 'wb')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['linkmd5id'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['linkmd5id'])
            return item


class MySQLPipeline(object):

    def open_spider(self, spider):
        # 打开数据库连接
        self.db = MySQLdb.connect("localhost","root","root123","footballhub",charset="utf8" )

    def close_spider(self, spider):
        # 关闭数据库连接
        self.db.close()

    def process_item(self, item, spider):
        if item['title'] is not None and item['posttime'] is not None and item['content'] is not None:

            # 使用cursor()方法获取操作游标
            cursor = self.db.cursor()
            # SQL 查询语句
            query = "SELECT id FROM article WHERE linkmd5id = '%s'" % (item['linkmd5id'])

            # print sql
            try:
                cursor.execute(query)
                if cursor.rowcount == 0:
                    stopwords = fenci.getStopWords()
                	arr = fenci.fenci(item['contentText'], stopwords)
                	#print 'contentWords:%s' % contentWords
                	contentWords = ' '.join(arr)

                    # SQL 插入语句
                    sql = "INSERT INTO article(title, \
                           posttime, source_url, source_name, content, \
                           content_text, link, linkmd5id, crawl_site, content_words) \
                           VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' )" % \
                           (item['title'], item['posttime'], item['sourceUrl'], item['sourceName'], \
                           item['content'], item['contentText'], item['link'], item['linkmd5id'], item['crawlSite'], contentWords)
                    # 执行sql语句
                    cursor.execute(sql)
                    # 提交到数据库执行
                    self.db.commit()
                    print("-------insert success--------")
                else:
                    print("-------duplicate link--------")
            except Exception as e:
               # 发生错误时回滚
               self.db.rollback()
               print("-------insert exception--------Error:%s" % e)

            return item
        else:
            raise DropItem("invalid item found: %s" % item)
