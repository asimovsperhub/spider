import json

import scrapy

from ..items import GeneralItem


class JSApp(scrapy.Spider):
    name = "jsapp"

    def start_requests(self):
        mantissa_dict = {
            1: "00000%d",
            2: "0000%d",
            3: "000%d",
            4: "00%d",
            5: "0%d",
            6: "%d",
        }
        for j in range(1, 10):
            for i in range(0, 999999):
                uid = str(j) + "000000" + mantissa_dict.get(len(str(i))) % i
                start_url = "https://api.jianshiapp.com/apiv1/user/info/other?uid=%s" % uid
                yield scrapy.Request(start_url, callback=self.parsing, cb_kwargs={"url": start_url})

    def parsing(self, rep, url):
        item = GeneralItem()
        data = json.loads(rep.text)
        if data.get("message") == "OK":
            username = data.get("data").get("display_name")
            if username != "见闻用户":
                item["username"] = username
                item["url"] = url
                yield item

