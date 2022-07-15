import json

import scrapy

from ..items import GeneralItem


class News_13(scrapy.Spider):
    name = "13_news"

    def __init__(self):
        self.url = "http://47.244.147.177:30000/news?page=%d&rows=30&newstype=all"

    def start_requests(self):
        url = self.url % 1
        yield scrapy.Request(url, callback=self.parse, dont_filter=True)

    def parse(self, response, **kwargs):
        data = json.loads(response.text).get("data")
        if data:
            total = data.get("total")
            if int(total) > 0:
                total_is = int(total) / 30
                if isinstance(total_is, float):
                    pages_ = int(total_is) + 2
                else:
                    pages_ = int(total_is) + 1
                for page in range(1, pages_):
                    yield scrapy.Request(self.url % page, callback=self._parse)

    def _parse(self, response, **kwargs):
        item = GeneralItem()
        data = json.loads(response.text).get("data")
        if data:
            for obj in data.get("list"):
                item["url"] = obj.get("source_link")
                item["username"] = obj.get("content")
                yield item
