import json

import scrapy

from ..items import GeneralItem


class Y(scrapy.Spider):
    name = "38_Y"

    def __init__(self):
        self.liver_id = set()

    def start_requests(self):
        for day in ["dayrich.html", "daycharm.html"]:
            day_rank = "https://zhibo.lvdou66.com/weblive/rank/%s" % day
            for i in ["0", "-1"]:
                day_data = {
                    "uid": "0", "day": "%s" % i
                }
                yield scrapy.FormRequest(day_rank, callback=self.parse, method='POST', formdata=day_data,
                                         dont_filter=True)
        for week in ["richweek.html", "charmweek.html"]:
            week_rank = "https://zhibo.lvdou66.com/weblive/rank/%s" % week
            week_data = {
                "uid": "0", "lastweek": "0"
            }
            yield scrapy.FormRequest(week_rank, callback=self.parse, method='POST', formdata=week_data,
                                     dont_filter=True)

    def parse(self, response, **kwargs):
        item = GeneralItem()
        guard = json.loads(response.text)
        if guard.get("ranklist"):
            for data in guard.get("ranklist"):
                if data.get("uid") not in self.liver_id:
                    liver_id = data.get("uid")
                    liver_name = data.get("nickname")
                    item["username"] = liver_name
                    item["url"] = liver_id
                    room_rank_url = "https://zhibo.lvdou66.com/weblive/rank/guard.html"
                    for type_ in ["0", "1", "3"]:
                        for page_ in range(50):
                            room_data = {
                                "user": str(liver_id),
                                "page": "%s" % page_,
                                "type": "%s" % str(type_),
                            }
                            yield scrapy.FormRequest(room_rank_url, callback=self._parse, method='POST',
                                                     formdata=room_data,
                                                     dont_filter=True)

    def _parse(self, response, **kwargs):
        item = GeneralItem()
        room = json.loads(response.text)
        if room.get("ranklist"):
            for data in room.get("ranklist"):
                item["username"] = data.get("nickname")
                item["url"] = "https://yabolive.com/" + str(data.get("uid"))
                yield item
