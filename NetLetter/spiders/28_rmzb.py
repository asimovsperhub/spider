import json

import scrapy

from ..items import GeneralItem


class RemaoZb(scrapy.Spider):
    name = "28_rmzb"

    def start_requests(self):
        url = "https://api.yuanbobo.com/v1/user/%d?mod=HUAWEIGRA-UL00&lan=0&sdk=9.4.5&source=2&token=5e3ae7be90a4a6a139ff31f5347912dc&query_source_id=74182633375941159&did=BCEBC1A49CB965F06A169B1B9BF7E28F&net=0&app=2&ts=1620465848401&bddid=VWHYX3JMZJ2CFJH22KLPGYRTZ75GXBA5WPHCYDSKIRAMVB5YBVOQ01&build=707&sys=android_5.0.1&bundle_id=qsbk.app.remix&review=0&source_id=375062570884698304&chn=qq&query_source=2&ver=9.4.7&sig=5c0a35a6fedd0955a02b1baef3a34566"
        for j in range(55443081, 60000000):
            url_ = url % j
            yield scrapy.Request(url_, callback=self.parse, cb_kwargs={"url": url_})

    def parse(self, response, **kwargs):
        item = GeneralItem()
        userinfo = json.loads(response.text).get("user", None)
        if userinfo:
            username = userinfo.get("name")
            url = kwargs.get("url")
            item["username"] = username
            item["url"] = url
            yield item
