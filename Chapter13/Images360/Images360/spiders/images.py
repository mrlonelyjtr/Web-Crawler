# 爬取360摄影美图，分别实现MongoDB存储、MySQL存储、Image图片存储的三个Pipeline
# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urlencode
import json
from Images360.items import Images360Item


class ImagesSpider(scrapy.Spider):
    name = 'images'
    allowed_domains = ['image.so.com']

    def start_requests(self):
        data = {'ch': 'photography', 'listtype': 'new'}
        base_url = 'http://image.so.com/zj?'
        
        for page in range(1, self.settings.get("MAX_PAGE") + 1):
            data['sn'] = page * 30
            url = base_url + urlencode(data)
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        result = json.loads(response.text)

        for image in result.get("list"):
            item = Images360Item()
            item['id'] = image.get("imageid")
            item['url'] = image.get("qhimg_url")
            item['title'] = image.get("group_title")
            item['thumb'] = image.get("qhimg_thumb_url")
            yield item
