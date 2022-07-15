import logging
import time

import scrapy

from ..component import read_top_excel
from ..items import GeneralItem
from ..mongo_ import MongoL, RedisL


class KY(scrapy.Spider):
    name = "oschina"

    def __init__(self):
        self.url_cache = set()

    def start_requests(self):
        # start_url = read_top_excel()
        for uid in range(2663968, 50000000):
            url = "https://my.oschina.net/u/%d" % uid
            # for url in start_url.get("oschina"):
            # uid = url.split("/")[-1]
            yield from self.mid(uid, url)

    def mid(self, uid, url):
        self.start = time.time()
        yield scrapy.Request(url, callback=self.fans_parsing, cb_kwargs={"uid": uid, "url": url})

    def fans_parsing(self, rep, uid, url):
        item = GeneralItem()
        if rep.status > 400:
            return
        self.url_cache.add(url)
        username = rep.selector.xpath(
            '//*[@id="mainScreen"]/div/div[1]/div/div[1]/div/div[1]/div[2]/h3/div/span/text()').get()
        item["username"] = username
        item["url"] = url
        yield item
        end = float(time.time())
        logging.info("Oschina One Spider Time : %s" % (end - self.start))

        fans_count = rep.selector.xpath(
            '//*[@id="mainScreen"]/div/div[1]/div/div[1]/div/div[1]/div[4]/div/a[1]/div[1]/text()').get()
        fans_count = fans_count.replace(" ", "").replace("\n", "")
        if fans_count:
            if "K" in fans_count:
                fanscount = float(fans_count.split("K")[0]) * 1000
            elif "W" in fans_count:
                fanscount = float(fans_count.split("W")[0]) * 10000
            else:
                fanscount = fans_count
            pages = int(fanscount) / 20
            if isinstance(pages, float):
                pages = int(pages) + 2
            else:
                pages = pages + 1
            for page in range(0, pages):
                fans_url = "https://my.oschina.net/u/%s/followers?sort=follow_time&p=%s" % (
                    uid, page)
                if fans_url.split("/followers")[0] not in self.url_cache:
                    yield scrapy.Request(fans_url, callback=self.nfans_parsing)

    def nfans_parsing(self, rep):
        fans_list = rep.selector.xpath('//*[@id="mainScreen"]/div/div/div/div[2]/div[3]/div[3]/div[1]/div')
        for fans in fans_list:
            # user_name = fans.xpath("./div[1]/div[1]/a//text()")[0].get()
            fans_url = fans.xpath(
                '//*[@id="mainScreen"]/div/div/div/div[2]/div[3]/div[3]/div[1]/div[1]/div[1]/div[1]/a/@href').get()
            uid = fans_url.split("/")[-1]
            yield from self.mid(uid, fans_url)
