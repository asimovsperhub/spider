import json
import logging
import time

import scrapy

from ..component import read_top_excel
from ..items import GeneralItem
from ..mongo_ import MongoL, RedisL

"""
用戶檢索接口  https://www.dgtle.com/search/user?search_word=%s&page=1 %search_words
"""


class DgtleSpider(scrapy.Spider):
    name = "dgtle"

    def __init__(self):
        self.item = GeneralItem()
        mongo = MongoL()
        _, self.mongo_col = mongo.mongo_col()
        conn_ = RedisL()
        self.conn_redis_ = conn_.conn_redis()

    def start_requests(self):
        start_url_list = read_top_excel()
        for start_url in start_url_list.get("dgtle"):
            # start_url = "https://www.dgtle.com/feed/interestedPerson"

            yield from self.find_next_fans_count(start_url.split("=")[-1])

    def find_next_fans_count(self, user_id):
        fans_count_url = "https://www.dgtle.com/user?uid=%s" % user_id
        yield scrapy.Request(fans_count_url, callback=self.find_next_fans, cb_kwargs={"user_id": user_id})

    def find_next_fans(self, rep, user_id):
        fans_count = rep.selector.xpath('/html/body/div[2]/div[3]/div/div[5]/div[1]/a[1]/span//text()').get()
        if fans_count:
            for page in range(int(fans_count[0]) + 1):
                fans_url = "https://www.dgtle.com/user/getMyFollowed/%s?page=%s" % (user_id, page)
                url = "https://www.dgtle.com/user?uid=%s" % user_id
                if self.conn_redis_.sadd("dgtle_url", str(url)) == 1:
                    self.start = float(time.time())
                    yield scrapy.Request(fans_url, callback=self.fans_parms)

    def fans_parms(self, rep):
        fans_list = json.loads(rep.text).get("data").get("dataList")
        if fans_list:
            for fans in fans_list:
                self.item["url"] = "https://www.dgtle.com/user?uid=%s" % fans.get("user_id")
                self.item["username"] = fans.get("username")
                yield self.item
                end = float(time.time())
                logging.info("DGTLE One Spider Time : %s" % (end - self.start))
                yield from self.find_next_fans_count(user_id=fans.get("user_id"))
                # yield self.item
