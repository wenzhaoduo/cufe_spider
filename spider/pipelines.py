# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
import json

from scrapy import signals
import codecs
from twisted.enterprise import adbapi
from datetime import datetime
from hashlib import md5
import MySQLdb
import MySQLdb.cursors

class JsonWriterPipeline(object):
    def __init__(self):
        self.file = open('0_0908.json','w')

    def process_item(self, item, spider):
        # item_list = ['bookName', item['bookName'], 'authorName', item['authorName'], 'callNo', item['callNo'],'isbnNo', item['isbnNo'],'pubName', item['pubName'],'pubYear', item['pubYear']]
        # line = json.dumps(item_list, ensure_ascii = False) + "\n"
        line = json.dumps(dict(item), ensure_ascii = False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()

class MySQLStoreCnblogsPipeline(object):
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('MySQLdb',
            host = 'localhost',
            db='cufedb',
            user='root',
            passwd='root',
            charset='utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode= False
        )

    #pipeline默认调用
    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self._do_insert, item, spider)
        return item
        
    #将每行写入数据库中
    def _do_insert(self, conn, item, spider):
        try:
            conn.execute('insert into bookinfo(callNo, bookName, authorName, pubName, pubYear, isbnNo) values (%s, %s, %s, %s, %s, %s)', 
                (item['callNo'], item['bookName'], item['authorName'], item['pubName'], item['pubYear'], item['isbnNo']))
        except:
            print ''.join(item['callNo'])

