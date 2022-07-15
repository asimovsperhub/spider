import scrapy

from ..items import GeneralItem


class Easou(scrapy.Spider):
    name = "39_easou"

    def start_requests(self):
        for i in range(0, 10000000000, 100):
            url = "https://book.easou.com/ta/waterfall.m?&start=%d&pageSize=100" % i
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        item = GeneralItem()
        root = response.xpath('body/li')
        for info in root:
            gid = info.xpath('./@gid').get()
            nid = info.xpath('./@nid').get()
            if gid and nid:
                url = "https://book.easou.com.cn/ta/novel.m?gid=%s&nid=%s" % (gid, nid)
                username = info.xpath('./div/div[2]/div[3]/text()').get()
                print(url, username)
                item['url'] = url
                item['username'] = username
                yield item
