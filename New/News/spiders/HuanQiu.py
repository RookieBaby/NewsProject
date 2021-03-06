# -*- coding: utf-8 -*-
import time,datetime
import requests
import uuid
import os

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..items import NewsItem
from ..file_model import File_mod


class HuanqiuSpider(CrawlSpider):
    name = 'HuanQiu'
    # allowed_domains = ['www.huanqiu.com/']
    start_urls = [
        'http://world.huanqiu.com/',
        'http://mil.huanqiu.com/',
        'http://finance.huanqiu.com/',
        'http://tech.huanqiu.com/',
        'http://auto.huanqiu.com/',
        'http://ent.huanqiu.com/',
        'http://go.huanqiu.com/',
        'http://lx.huanqiu.com/',
        'http://hope.huanqiu.com/',
        'http://society.huanqiu.com/',
        'http://cul.huanqiu.com/'
    ]

    rules = (
        # Rule(LinkExtractor(allow=r'http://[a-z]{2,7}\.huanqiu.com/$'), follow=True),
        Rule(LinkExtractor(allow=r'http://[a-z]{2,7}\.huanqiu.com/[a-z]{3,17}/$'), follow=True),
        Rule(LinkExtractor(allow=r'http://[a-z]{2,7}\.huanqiu.com/(\w+)/2018-[0-9]{2}/(\d+).html'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item = NewsItem()
        link = response.url.split('.huanqiu.com')
        ll = link[1].split('/2018')[0]
        if 'http://world' == link[0] or 'http://oversea' == link[0]:
            if '/photo' == ll:
                item['NewsCategory'] = ''
            else:
                item['NewsCategory'] = '001.020'  # 国际
        elif 'http://finance' == link[0]:
            if '/financepic' == ll:
                item['NewsCategory'] = ''
            else:
                item['NewsCategory'] = '001.007'  # 财经
        elif 'http://mil' == link[0]:
            if '/gt' == ll or '/milmovie' == ll:
                item['NewsCategory'] = ''
            else:
                item['NewsCategory'] = '001.011'  # 军事
        elif 'http://tech' == link[0]:
            if '/photo' == ll or '/video' == ll:
                item['NewsCategory'] = ''
            else:
                item['NewsCategory'] = '001.006'  # 科技
        elif 'http://auto' == link[0]:
            item['NewsCategory'] = '001.008'  # 汽车
        elif 'http://ent' == link[0]:
            item['NewsCategory'] = '001.005'  # 娱乐
        elif 'http://go' == link[0]:
            if '/vision' == ll:
                item['NewsCategory'] = ''
            else:
                item['NewsCategory'] = '001.017'  # 旅游
        elif 'http://lx' == link[0]:
            item['NewsCategory'] = '001.026'  # 教育
        elif 'http://hope' == link[0]:
            item['NewsCategory'] = '001.033'  # 公益
        elif 'http://cul' == link[0]:
            if '/comic' == ll:
                item['NewsCategory'] = ''
            else:
                item['NewsCategory'] = '001.036'  # 文化
        elif 'http://society' == link[0]:
            if '/photonew' == ll:
                item['NewsCategory'] = ''
            else:
                item['NewsCategory'] = '001.009'  # 社会
        else:
            item['NewsCategory'] = ''
        i = datetime.datetime.now()
        b = "%s0%s" % (i.year, i.month)
        item['NewsID'] = '{0}-'.format(b) + str(uuid.uuid1())
        NewsTitle = response.xpath('//div[@class="con"]/div/div[@class="l_a"]/h1/text() | //div[@class="focus_box"]/h1/strong/text()').extract_first()
        if NewsTitle is not None:
            item['NewsTitle'] = NewsTitle
        else:
            item['NewsTitle'] = response.xpath('//div[@class="conText"]/h1/text()').extract_first()
        NewsDate = response.xpath('//div[@class="con"]/div/div[@class="l_a"]/div/span[@class="la_t_a"]/text()').extract_first()
        if NewsDate is not None:
            item['NewsDate'] = NewsDate
        else:
            item['NewsDate'] = response.xpath(
                '//div[@class="summaryNew"]/strong[@class="timeSummary"]/text() | //ul/li[@class="time"]/div/span/text()'
            ).extract_first()
        item['NewsRawUrl'] = response.url
        SourceName = response.xpath(
            '//div[@class="conText"]//a/text() | '
            '//div[@class="la_tool"]/span/a/text() | '
            '//li[@class="from"]/div[@class="item"]/span/text()'
        ).extract_first()
        if SourceName is not None:
            item['SourceName'] = SourceName
        else:
            item['SourceName'] = '环球网'

        item['AuthorName'] = response.xpath(
            '//div[@id="text"]/div[last()]/span/text() | '
            '//div[@class="la_edit"]/span/text() | '
            '//li[@class="user"]/div[@class="item"]/span/text() |'
            '//div[@class="editorSign"]/span[@id="editor_baidu"]/text()'
        ).extract_first()[3:6]
        SourceCategory = response.xpath('//div[@class="nav"]/div[@class="nav_left"]/a[3]/text()').extract_first()
        if SourceCategory is not None:
            item['SourceCategory'] = '环球' + SourceCategory
        else:
            item['SourceCategory'] = '环球滚动新闻'
        item['NewsType'] = 0
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        # 获取图片链接
        image_urls = response.xpath(
            '//div[@class="la_con"]/p//img/@src | '
            '//div[@id="text"]//p//img/@src | '
            '//div[@class="m_l"]//a/img/@src'
        ).extract()
        try:
            content = ''.join(response.xpath(
                    '//div[@class="la_con"]/p |'
                    '//div[@id="text"]/p |'
                    '//div[@id="text"]/div/p |'
                    '//div[@class="m_l"]//a/img'
                ).extract())
        except:
            content = 'None'
        listFiles = []
        if image_urls:
            for image_url in image_urls:
                if '?' in image_url:
                    image_url_new = image_url.split('?')[0]
                else:
                    image_url_new = image_url
                response_url = response.url
                a = File_mod(image_url_new, content, response_url)
                content = a.detail_file()
                if 'v1' in image_url:
                    full_name = a.Download_video()
                else:
                    full_name = a.Download_image()
                filemodel = {}
                filemodel['FileID'] = str(uuid.uuid1())
                filemodel['FileType'] = 0
                filemodel['FileDirectory'] = a.detail_fdfs_file(full_name)
                filemodel['FileDirectoryCompress'] = a.detail_fdfs_file(full_name)
                filemodel['FileDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                filemodel['FileLength'] = a.detail_FileLength(full_name)
                filemodel['FileUserID'] = None
                filemodel['Description'] = None
                filemodel['NewsID'] = item['NewsID']
                filemodel['image_url'] = image_url
                listFiles.append(filemodel)
                a.Delete_image(full_name)

        item['NewsContent'] = content
        item['FileList'] = listFiles

        yield item
