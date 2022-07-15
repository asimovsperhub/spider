import base64

import scrapy

from ..items import GeneralItem


class Loovee(scrapy.Spider):
    name = "loovee"

    def __init__(self):
        self.item = GeneralItem()

    def start_requests(self):
        for i in range(1, 600000000):
            uid_base64 = str(base64.encodebytes(bytes('%s' % i, 'utf-8')), encoding='utf-8')
            url = "https://dmwww.loovee.com/user/home/%s" % uid_base64
            yield scrapy.Request(url, callback=self.parsing, cb_kwargs={"url": url})

    def parsing(self, rep, url):
        if rep.status == 200:
            username_xpath = '//*[@id="container"]/div[1]/div[1]/div[2]/div[1]/span[1]/text()'
            username = rep.xpath(username_xpath).get()
            if username:
                self.item["username"] = username
                self.item["url"] = url
                yield self.item
