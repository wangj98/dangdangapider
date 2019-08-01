# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DangdangspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    cate1 = scrapy.Field()
    cate2 = scrapy.Field()
    cate3 = scrapy.Field()
    aid = scrapy.Field()
    item_name = scrapy.Field()
    price = scrapy.Field()
    store_name = scrapy.Field()
    picture_name = scrapy.Field()

    img_urls = scrapy.Field()
    img_url = scrapy.Field()

