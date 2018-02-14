from scrapy.conf import settings
from urllib import urlencode
from scrapy import Request

import scrapy
from scrapy.item import Item, Field
import re
import json


class SiteProductItem(Item):
    Title = Field()
    Price = Field()
    Product_Url = Field()


class NewEvents (scrapy.Spider):
    name = "scrapingdata"
    allowed_domains = ['demo.api2cart.com']
    # start_urls = ['https://coinmarketcap.com/all/views/all/']

    LOGIN_URL = 'https://app.api2cart.com/login/login'
    API_URL = 'https://app.api2cart.com/stores/data?_dc=1515986395368&page=1&start=0&limit=30'

    form_data = {'account_email': 'info@web-company.nl', 'account_password': 'IGUvbkjtoi2hgWE@'}
    headers = {'Referer': 'https://app.api2cart.com/stores',
               'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/62.0.3202.75 Safari/537.36',
               'X-Requested-With': 'XMLHttpRequest',
               'Content-Type': 'application/x-www-form-urlencoded'
               }

    settings.overrides['ROBOTSTXT_OBEY'] = False

    def start_requests(self):
        yield Request(url=self.LOGIN_URL,
                      callback=self._parse_data,
                      headers=self.headers,
                      method='POST',
                      body=urlencode(self.form_data),
                      dont_filter=True
                      )

    def _parse_data(self, response):

        return Request(
            url=self.API_URL,
            headers=self.headers,
            dont_filter=True,
            callback=self._parse_product_links
        )

    def _parse_product_links(self, response):

        stores = []
        prods = []
        try:
            data = json.loads(response.body)
            stores = data.get('stores')
        except:
            self.log('Json Error')
        for store in stores:
            prods.append(store.get('store_url'))

        for prod in prods:
            yield Request(url=prod, callback=self.parse_product)

    def parse_product(self, response):
        prod_item = SiteProductItem()
        title = self._parse_title(response)
        price = self._parse_price(response)
        url = self._parse_url(response)
        prod_item['Title'] = title
        prod_item['Price'] = price
        prod_item['Product_Url'] = url
        return prod_item

    @staticmethod
    def _parse_title(response):
        title = response.xpath('//ul[@class="thumb-container"]/li[@class="item first"]/a/@href').extract()

        return title

    @staticmethod
    def _parse_price(response):
        price = response.xpath('//ul[@class="thumb-container"]/li[@class="item first"]/a/@href').extract()
        return price

    @staticmethod
    def _parse_url(response):
        url = response.xpath('//ul[@class="thumb-container"]/li[@class="item first"]/a/@href').extract()

        return url