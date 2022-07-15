import json

import scrapy

from ..items import GeneralItem


class Zflive(scrapy.Spider):
    name = "43_zflive"

    def start_requests(self):
        url = "http://47.100.43.70/channeltypes/all"

        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        root = response.xpath('/html/body/div[1]/div[3]/div[2]/div[2]/ul/li')
        for ci in root:
            cid = ci.xpath('./a/@href').get().replace("/", "")
            fansrank = "https://47.100.43.70/live-rank/fansrank/get"
            liver = "http://47.100.43.70/live-channel-info/channel/v2/info?cid=%s" % cid
            yield scrapy.FormRequest(fansrank, callback=self._rank_parse, method='POST', formdata={"cid": cid},
                                     dont_filter=True)
            yield scrapy.Request(liver, callback=self.live)

    def _rank_parse(self, response, **kwargs):
        item = GeneralItem()
        data = json.loads(response.text)
        week = data.get("week")
        day = data.get("day")
        all_ = list(week) + list(day)
        for day_ in all_:
            item["username"] = day_.get("uname")
            item["url"] = "https://www.zhuafan.live/" + str(day_.get("uid"))
            yield item

    def live(self, response, **kwargs):
        item = GeneralItem()
        data = json.loads(response.text)
        if data:
            item["username"] = data.get("uname")
            item["url"] = response.url
            yield item
