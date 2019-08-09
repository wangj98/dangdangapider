# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
import pymysql
import codecs
import pymysql.cursors
from twisted.enterprise import adbapi
from DangdangSpider.items import DangdangspiderItem

from DangdangSpider.settings import IMAGES_STORE as images_store
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.project import get_project_settings
import os
import re
import hashlib

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
#         数据存入数据库中


class DangdangspiderImagePipeline(ImagesPipeline):


    def get_media_requests(self, item, info):
        """
        将连接传到下一级
        :param item:
        :param info:
        :return:
        """
        for img_url in item['img_urls']:
            item['img_url'] = img_url
            # 该图片连接存入item为图片命名做准备
            item_name = item['item_name']
            cate1 = item['cate1']
            item = DangdangspiderItem(img_url=img_url, item_name=item_name, cate1=cate1)
            yield scrapy.Request(url=img_url, meta={'item': item})


    def file_path(self, request, response=None, info=None):
        """
        下载图片
        :param request:
        :param response:
        :param info:
        :return:
        """
        item = request.meta['item']
        sha1 = item['img_url']

        # item_name = (item['item_name']).replace('/', '_').replace('|', '_').replace('*', '').replace(':', '_')
        cate1 = (item['cate1']).replace('图书', 'book').replace('音像/杂志', 'Audiovisual_magazine').replace('电子书/网文/听书', 'E-books_web texts_listening books').replace('男女装/内衣', 'Men and women wear_underwear').replace('鞋', 'shoes').\
            replace('运动户外', 'Exercise outdoors').replace('箱包皮具', 'Luggage leather').replace('当当优品', 'dangdang_superior products').replace('母婴用品', ' maternal and infant supplies').replace('孕妈专区', 'Pregnant mother zone').replace('童装童鞋', 'Children wear children shoes').replace('玩具童车', 'The toy stroller').\
            replace('家居家纺', 'Household textile').replace('家具/家装/家饰', 'Furniture_home decoration_decoration').replace('汽车用品', 'automobile accessories').replace('时尚美妆', 'Fashionable beauty makeup').replace('珠宝饰品', 'jewelry').replace('手表/眼镜/礼品', 'Watch_glasses_gift').replace('食品', 'food').\
            replace('健康/营养/保健', 'Health_nutrition_health care').replace('手机通讯', 'Mobile communications').replace('数码影音', 'Digital audio').replace('电脑办公', 'computer_office').replace('家用电器', 'household appliances').replace('大家电', 'Large Appliance').replace('海外购', 'Accesories').\
            replace('地方特色', 'local_feature').replace('文化创意用品', 'Cultural and creative supplies')
        #  将分类转化英文
        # cate2 = (item['cate2']).replace('/', '_')
        # cate3 = (item['cate3']).replace('/', '_')
        sha1 = hashlib.sha1()
        sha1.update(item['img_url'].encode('utf8'))
        # 将URL转化为哈希值当做图片名
        apath = "./" + cate1 + '/'
        path = apath + sha1.hexdigest() + '.jpg'
        # 存储路径

        return path

    def item_completed(self, results, item, info):
        # 图片下载完成后，返回的结果results
        print(results)
        return item


