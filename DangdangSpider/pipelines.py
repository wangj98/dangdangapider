# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
import codecs
import pymysql
import pymysql.cursors
from twisted.enterprise import adbapi

from scrapy.pipelines.images import ImagesPipeline
from DangdangSpider.settings import IMAGES_STORE as images_store
from scrapy.utils.project import get_project_settings
import os
from DangdangSpider.items import DangdangspiderItem
import re

class DangdangspiderPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=False,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        return item

    def _conditional_insert(self, tx, item):
        sql = """insert into item_data(cate1, cate2, cate3, aid, item_name, price, store_name, picture_name) 
        values(%s, %s, %s, %s, %s, %s, %s, %s)"""
        params = (item['cate1'], item['cate2'], item['cate3'], item['aid'], item['item_name'], item['price'],
                  item['store_name'], item['picture_name'])
        tx.execute(sql, params)

class DangdangspiderIamgePipeline(ImagesPipeline):
    img_store = get_project_settings().get('IMAGES_STORE')


    def get_media_requests(self, item, info):
        for img_url in item['img_urls']:
            item = DangdangspiderItem()
            item['img_url'] = img_url
            item_name = item['item_name']
            item = DangdangspiderItem(img_url=img_url, item_name=item_name)

            yield scrapy.Request(url=img_url, meta={'item': item})


    def file_path(self, request, response=None, info=None):
        item = request.meta['item']
        img_url = item['img_url']
        print('2434res-----------')

        item_name = (item['item_name']).replace('/', '_').replace('|', '_').replace('*', '')
        print('-------------------------efwe----')
        cate1 = (item['cate1']).replace('/', '_')
        cate2 = (item['cate2']).replace('/', '_')
        cate3 = (item['cate3']).replace('/', '_')

        apath = "./" + cate1 + '/' + cate2 + '/' + cate3 + '/' + item_name
        path = apath + '/'  + '.jpg'
        return path

    def item_completed(self, results, item, info):
        # 图片下载完成后，返回的结果results
        print(results)
        return item


