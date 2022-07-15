import json

import scrapy

from ..items import GeneralItem


class KGQQ(scrapy.Spider):
    name = "27_kg_qq"

    def start_requests(self):
        for i in range(52178446, 999999999):
            url = "https://node.kg.qq.com/webapp/proxy?ns=proto_vip_webapp&cmd=vip.get_vip_info&t_uUid=%d" % i
            yield scrapy.Request(url, callback=self.parse, cb_kwargs={"url": url})

    def parse(self, response, **kwargs):
        item = GeneralItem()
        # response.encoding = "utf-8"
        userinfo = json.loads(response.text).get("data")
        if userinfo:
            username = userinfo.get("vip.get_vip_info").get("stUserInfo").get("strNick")
            item["username"] = username
            item["url"] = kwargs.get("url")
            yield item
