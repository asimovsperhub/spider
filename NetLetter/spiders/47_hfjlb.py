import scrapy
from NetLetter.items import GeneralItem

# 花粉俱乐部


class QuotesSpider(scrapy.Spider):
    name = "hfjlb"

    def start_requests(self):
        url = "https://club.huawei.com/space-uid-%s.html"
        # for i in range(3950, 239999999):
        for i in range(5344764, 239999999):
            # for i in range(200, 1000):
            link = url % i
            yield scrapy.Request(link, callback=self.parse,  cb_kwargs={"uid": str(i)})

    def parse(self, response, uid):
        username = response.css('.pcb-name::text').get()
        if not(username) or '花粉' + uid == username or 'huafen'+uid == username:
            return
        item = GeneralItem()
        item['username'] = username
        item['url'] = response.url
        yield item
