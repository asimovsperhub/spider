import scrapy

from ..items import GeneralItem


class Moshen(scrapy.Spider):
    name = "23_moshen"

    def start_requests(self):
        for i in range(0, 99999999):
            url = "http://m.yilian521.com/weixin_share/users.php?userid=&share_userid=&userid=169900%d" % i
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        item = GeneralItem()
        username = response.xpath('/html/body/div[1]/div[4]/div[1]/p').get()
        if "</p>" in username:
            username = username.split(">")[1].split("<")[0]
        if username:
            item['username'] = username
            item['url'] = response.url
            yield item
