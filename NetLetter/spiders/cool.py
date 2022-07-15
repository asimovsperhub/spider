import scrapy

from ..items import GeneralItem


class Cool(scrapy.Spider):
    name = "cool"

    def start_requests(self):
        mantissa_dict = {
            1: "00000%d",
            2: "0000%d",
            3: "000%d",
            4: "00%d",
            5: "0%d",
            6: "%d",
        }
        for i in range(1, 10):
            for j in range(999999):
                uid = str(i) + mantissa_dict.get(len(str(j))) % j
                url = "https://www.coolapk.com/u/%s" % uid
                yield scrapy.Request(url, callback=self.parsing, cb_kwargs={"url": url})

    def parsing(self, rep, url):
        item = GeneralItem()
        content = rep.xpath('/html/body/div/div[2]/div/div[1]/text()').get()
        print(content)
        if content:
            username = content.split("「")[-1].split("」")[0]
            item["url"] = url
            item["username"] = username
            yield item

