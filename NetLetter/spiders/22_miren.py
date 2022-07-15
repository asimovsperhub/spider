import json
import time

import scrapy
from scrapy.core import engine
from scrapy.utils import spider

from ..mongo_ import RedisL
from ..items import GeneralItem
from ..javadecode import Mrzb


class Miren(scrapy.Spider):
    name = "22_miren"

    def __init__(self):
        self.m = Mrzb()
        conn_ = RedisL()
        self.conn_redis_ = conn_.conn_redis()

    def start_requests(self):
        url = "https://zhibo.ishuaji.cn/zone/zonedata.html"
        for i in range(27280604, 99999999):
            data = self.m.data()
            if not data:
                self.crawler.engine.pause()
                time.sleep(600)
                self.crawler.engine.unpause()
                spider.logger.info("request body  get failed  pause  600 s")
                data = self.m.data()
                spider.logger.info("retry get data:%s" % data)
            if data:
                spider.logger.info("decode request  body:%s" % (data % i))
                self.conn_redis_.set("mrzb_uid", i)
                yield scrapy.FormRequest(url, callback=self.parse, method='POST',
                                         body=data % i, cb_kwargs={"__id": i}, dont_filter=True)

    def parse(self, response, **kwargs):
        item = GeneralItem()
        javadecodedata = self.m.decode(response.text)
        if javadecodedata:
            msg = json.loads(self.m.decode(response.text))
            # print("response msg:%s" % msg)
            # spider.logger.info("response status:%s" % response.status_code)
            spider.logger.info("response msg:%s" % msg)
            if not msg or msg.get("code") != 1:
                return
            data = msg.get("data")
            if data:
                item["username"] = data.get("sign")
                item["url"] = kwargs.get("__id")
                yield item
