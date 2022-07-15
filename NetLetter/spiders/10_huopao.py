import scrapy

from ..items import GeneralItem


class HP(scrapy.Spider):
    name = "10_huopao"

    def start_requests(self):
        for i in range(1100, 1500):
            url = "http://share.ishuaji.cn/share/livenew/%d.html" % i
            yield scrapy.Request(url, callback=self.parse, cb_kwargs={"uid": i})

    def parse(self, response, **kwargs):
        item = GeneralItem()
        username = response.xpath("/html/body/section/div[2]/div[2]/h2/text()").get()
        print(username)
        if username:
            url = "http://share.ishuaji.cn/share/livenew/%s.html" % kwargs.get("uid")
            item["username"] = username
            item["url"] = url
            yield item
