import scrapy

from ..items import GeneralItem


class Fdd(scrapy.Spider):
    name = "08_fdd"

    def start_requests(self):
        for i in range(3505750, 9999999):
            url = 'https://www.fangdd.com/agent/%d/profile' % i
            yield scrapy.Request(url, callback=self.parse, dont_filter=True, meta={
                'dont_redirect': True,
                'handle_httpstatus_list': [302]
            })

    def parse(self, response, **kwargs):
        if response.status > 400:
            return
        item = GeneralItem()
        username = response.xpath('//*[@id="root"]/main/div[1]/div[2]/div[1]/span/text()').get()
        if not username:
            return
        item["username"] = username
        item["url"] = response.url
        yield item
