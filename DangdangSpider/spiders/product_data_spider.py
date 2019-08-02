# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
import re
from DangdangSpider.items import DangdangspiderItem


class ProductDataSpiderSpider(scrapy.Spider):
    name = 'product_data_spider'
    # allowed_domains = ['http://category.dangdang.com/']
    start_urls = ['http://category.dangdang.com/']
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        # 'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        # 'Connection': 'keep-alive',
        'Referer': 'http://category.dangdang.com/',
        # 'User-Agent': 'Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50',
    }

    def parse(self, response):
        """
        当当全部商品下的小分类链接
        :param response:
        :return:
        """
        html = Selector(response)
        allid = html.xpath("//*[@id]/div/ul/li[@name]/a/@href").extract()
        # 小分类链接地址
        for cate_url in allid:
            yield scrapy.Request(url=cate_url, callback=self.parse_url, headers=self.header)

    def parse_url(self, response):
        """
        小分类下每个产品的链接
        :param response:
        :return:
        """
        html1 = Selector(response)
        qid = html1.xpath("//ul[@class= 'bigimg cloth_shoplist']/li/@id").extract()
        # print(qid)
        item = DangdangspiderItem()
        if qid != None:
            # 小分类有产品即进入，没有产品则到下一个小分类
            for aid in qid:
                item['aid'] = int(aid)
                item = DangdangspiderItem(aid=aid)
                base_url = 'http://product.dangdang.com/'
                item_url = base_url + aid + '.html'
                # 获取每个产品的链接
                yield scrapy.Request(url=item_url, callback=self.parse_item, headers=self.header, meta={'item': item})

            next_link = html1.xpath("//*[@id='12810']/div[3]/div[2]/div/ul/li[10]/a/@href").extract_first()
            next_baseurl = 'http://category.dangdang.com'
            if next_link != None:
                next_url = next_baseurl + next_link
                # 获取该小分类下一页的地址，自身循环
                yield scrapy.Request(url=next_url, callback=self.parse_url, headers=self.header, meta={'item': item})

    def parse_item(self, response):
        """
        每个商品信息
        :param response:
        :return:
        """
        item_url = Selector(response)
        item = response.meta['item']

        cate1 = ','.join(item_url.xpath("//*[@id='breadcrumb']/a[1]/b/text()").extract())
        item['cate1'] = cate1
        # print(cate1)

        cate2 = ','.join(item_url.xpath("//*[@id='breadcrumb']/a[2]/text()").extract())
        item['cate2'] = cate2
        # print(cate2)

        cate3 = ','.join(item_url.xpath('//*[@id="breadcrumb"]/a[3]/text()').extract())
        item['cate3'] = cate3
        # print(cate3)

        price = ','.join(item_url.xpath("//*[@id='dd-price']/text()").extract()).replace(' ', '').replace(',',
                                                                                                          '').replace(
            '\n', '')
        item['price'] = price
        # print(price)

        item_name = ','.join(item_url.xpath("//*[@id='product_info']/div[1]/h1/text()").extract()).replace(' ',
                                                                                                           '').replace(
            '\n', '').replace('\r', '')
        item['item_name'] = item_name
        # print(item_name)

        store_name = ','.join(item_url.xpath("//*[@id='service-more']/div[2]/p[1]/span/span[2]/a/@title").extract())
        item['store_name'] = store_name
        # print(store_name)

        picture_name = item_url.xpath("//*[@id='main-img-slider']/li/a/@data-imghref").extract()
        item['picture_name'] = picture_name
        # 产品各种参数
        aid = item['aid']
        item = DangdangspiderItem(aid=aid, cate1=cate1, cate2=cate2, cate3=cate3, price=price, item_name=item_name,
                                  store_name=store_name, picture_name=picture_name)

        a = ','.join(item_url.xpath("/html/body/script[1]/text()").extract()).replace('\n', '')
        productId = str(re.findall('"productId":"(\d*)', a))
        categoryPath = str(re.findall('"categoryPath":"(.*?)"', a))
        describeMap = str(re.findall('"describeMap":"(.*?)"', a))
        shopid = str(re.findall('"shopId":"(\d*)', a))
        # 每个商品下面的大图片需要调到下一个链接才能获取，从该产品自身中使用正则表达式拼接出下一个链接所需的参数

        bigimg_url = "http://product.dangdang.com/index.php?r=callback%2Fdetail&productId=" + productId + "&templateType=mall&describeMap=" + describeMap + "&shopId=" + shopid + "&categoryPath=" + categoryPath
        bigimg_url = bigimg_url.replace("[", "").replace("]", "").replace("'", "")
        # 大图的链接
        yield scrapy.Request(url=bigimg_url, callback=self.parse_bigimg, headers=self.header, meta={'item': item})

    def parse_bigimg(self, response):
        """
        获取大图，并对其中图片进行处理
        :param response:
        :return:
        """
        html = Selector(response)
        item = response.meta['item']
        bigimg = html.xpath('/html/body//img/@data-original').extract()
        picture_name = item['picture_name']

        if isinstance(bigimg,str):
            picture_name.append(bigimg)
            print('-----------------------')
        elif isinstance(picture_name, str):
            bigimg.append(picture_name)
            picture_name = bigimg
        else:
            picture_name = picture_name + bigimg
        img_urls = picture_name
        img_urls = list(filter(None, img_urls))
        item['img_urls'] = img_urls
        # 将每个产品上面的大图（可由该产品网址直接获得）和下面的大图（需要跳转到下个网页）存到一个数组中（方便下载图片）
        picture_name = ','.join(picture_name)
        item['picture_name'] = picture_name
        # 将该数组转化为字符串方便存入数据库

        yield item