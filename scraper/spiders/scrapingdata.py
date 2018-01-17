from scrapy.conf import settings
from urllib import urlencode
from scrapy import Request

import scrapy
from scrapy.item import Item, Field
import re
import json


class SiteProductItem(Item):
    Name = Field()
    Symbol = Field()
    MarketCap = Field()
    Price = Field()
    CirculatingSupply = Field()
    Volume = Field()
    Percent_1h = Field()
    Percent_24h = Field()
    Percent_7d = Field()


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
        fields = [
            'Name',
            'Symbol',
            'MarketCap',
            'Price',
            'CirculatingSupply',
            'Volume',
            'Percent_1h',
            'Percent_24h',
            'Percent_7d'
        ]

        # trs = response.xpath('//table//tbody//tr[@id]')
        # for tr in trs:
        #     item = EventItem()
        #     for i in range(1, 10):
        #         value = [
        #             val.strip()
        #             for val in tr.xpath('.//td[position()={position} and a]/a/text() |'
        #                                 ' .//td[position()={position}]/text()'.format(position=i+1)).extract()
        #             if val.strip()
        #         ]
        #         item[fields[i-1]] = value[0].replace('?', '').replace('*', '') if value else u''
        #     yield item

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
            prod_item = SiteProductItem()
            req = Request(
                prod,
                callback=self.parse_product,
                meta={
                    "product": prod_item,
                },
                dont_filter=True,
            )
            yield req

    def parse_product(self, response):
        data = response.body
        return data