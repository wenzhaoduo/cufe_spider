# -*- coding: utf8 -*-
# ----------------------------程序说明------------------------------------
# 这个程序可以自动换索书号就行索引

from scrapy.selector import Selector
from spider.items import BookItem,URLItem,NextPageItem
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
from scrapy.utils.url import urljoin_rfc
import sys
import time
import re


class CufeSpider(CrawlSpider):
    name = "cufe"
    handle_httpstatus_list = [500]  #让scrapy处理http返回状态消息为500的response

    #由索书号构成爬虫的初始网址
    callnolist = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-/*'
    frontUrl = "http://202.205.213.113:8080/opac/openlink.php?strSearchType=callno&match_flag=forward&historyCount=1&strText="
    lastUrl ="&doctype=01&displaypg=20&showmode=list&sort=CATA_DATE&orderby=desc&dept=ALL"

    def start_requests(self):
        #不断生成索书号进行索引
        for i in range(0,len(self.callnolist)):
            yield Request(self.frontUrl+self.callnolist[i]+self.lastUrl,callback=self.myparse)

    # extract the infomation we need
    def myparse(self, response):       
        reload(sys)
        sys.setdefaultencoding('utf-8')

        curCall = ''.join(re.findall('strText=[A-Z0-9\*\/\.\-]+',''.join(response.url)))
        curCall_list = curCall.split('=')

        if(response.status == 500):     #需要扩展索书号分支
            print "open callNo="+''.join(curCall_list[1])+" failed. Augment branches..."
            for i in range(0,len(self.callnolist)):
                yield Request(self.frontUrl+''.join(curCall_list[1])+self.callnolist[i]+self.lastUrl,callback=self.myparse)

        else:   #不需要扩展索书号分支
            sel = Selector(response)
            sites = sel.xpath('//ol/li')

            if(curCall != '' and len(sites) != 0):
                print "callNo="+''.join(curCall_list[1])+" page=1 is crawling..."
            elif(len(sites) == 0):
                print "callNo="+''.join(curCall_list[1])+" does not exist."

            items = []
            urlitems = []

            for site in sites:
                bookName_list = site.xpath('h3/a/text()').extract() #提取书名
                callNo_list = site.xpath('h3/text()').extract()     #提取索书号
                mixed = site.xpath('p/text()').extract()            #包含作者名字，出版社名字，出版年份

                str_bookName = re.sub('[0-9]{1,}\.','',(''.join(bookName_list)),count = 1, flags=re.I)
                str_callNo = ''.join(callNo_list)
                str_mixed = ''.join(mixed)
                str_temp = str_mixed.split('\n')
                str_authorName = ''.join(str_temp[0])

                str_pubName = ''
                str_pubYear = ''
                for i in range(1,len(str_temp)):
                    if((''.join(str_temp[i])).strip() != ''):
                        str_temp1 = str_temp[i].split(u'\xa0')
                        if(len(str_temp1) == 2):
                            str_pubName = ''.join(str_temp1[0])
                            str_pubYear = ''.join(str_temp1[1])

                # 将提取的信息赋给item
                item = BookItem()
                item['bookName'] = str_bookName.strip()
                item['authorName'] = str_authorName.strip()
                item['pubName'] = str_pubName.strip()
                item['pubYear'] = str_pubYear.strip()
                item['callNo'] = str_callNo.strip()
                items.append(item)

                # 提取每一本书的详细信息的URL地址
                urlitem = URLItem()
                url_ISBN = site.xpath('h3/a/@href').extract()
                urlitem['url'] = urljoin_rfc('http://202.205.213.113:8080/opac/',''.join(url_ISBN))
                urlitems.append(urlitem)

            # 打开详细信息的网页
            for i in range(0,len(items)):
                yield Request(urlitems[i]['url'],meta={'item':items[i]},callback=self.parse_ISBN)

            # 提取下一页的URL地址
            url_nextpage_list = []
            pageInfo = sel.xpath('//*[@id="num"]/span/a')
            for page in pageInfo:
                textInfo = page.xpath('text()').extract()
                if ((''.join(textInfo)) == "下一页"):
                    url_nextpage_list = pageInfo.xpath('@href').extract()

            if (len(url_nextpage_list) == 1):
                url_nextpage = ''.join(url_nextpage_list[0])
            elif (len(url_nextpage_list) == 2):
                url_nextpage = ''.join(url_nextpage_list[1])
            else:
                url_nextpage = ''

            if(url_nextpage != ''): #若存在下一页，则跟进
                pageNo = re.findall('page=[0-9]{1,}', url_nextpage)
                curCall = ''.join(re.findall('callno=[A-Z0-9\*\/\.\-]+',url_nextpage))
                if(curCall != ''):
                    callNo_list = curCall.split('=')
                    print "callNo="+''.join(callNo_list[1])+" "+''.join(pageNo)+" is crawling..."
                else:
                    print "callNo=/ "+''.join(pageNo)+" is crawling..."

                url_nextpage = urljoin_rfc('http://202.205.213.113:8080/opac/openlink.php', ''.join(url_nextpage))
                yield Request(url_nextpage, callback=self.myparse)


    # 获取ISBN号，及补充索书号callNo
    def parse_ISBN(self,response):
        sel = Selector(response)
        item = response.meta['item']
        items = []
        sites = sel.xpath('//*[@id="item_detail"]/dl')
        isbnNo_list = []      #存放ISBN号
        for site in sites:
            pubInfo = site.xpath('dt/text()').extract()
            if((''.join(pubInfo)) == "ISBN及定价:"):
                isbnNo_list = site.xpath('dd/text()').re('[0-9]{1,}-[0-9]{1,}-[0-9]{1,}-[0-9]{1,}-[0-9]{1,}')
        item['isbnNo'] = ''.join(isbnNo_list)

        items.append(item)
        return items
