# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class SpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
	pass

class BookItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
	callNo = scrapy.Field()
	bookName = scrapy.Field()
	authorName = scrapy.Field()
	pubName = scrapy.Field()
	pubYear = scrapy.Field()
	isbnNo = scrapy.Field()

class URLItem(scrapy.Item):
	url = scrapy.Field()

class NextPageItem(scrapy.Item):
	url = scrapy.Field()