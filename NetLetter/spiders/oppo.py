import json
import logging
import time

import scrapy

from ..component import read_top_excel
from ..items import GeneralItem
from ..mongo_ import MongoL, RedisL


class OppoSpiders(scrapy.Spider):
    name = "oppo"

    def __init__(self):
        mongo = MongoL()
        _, self.mongo_col = mongo.mongo_col()
        conn_ = RedisL()
        self.conn_redis_ = conn_.conn_redis()
    def start_requests(self):
        # 访客
        # start_url = "https://www.oppo.cn/member/index/visitor.json?page=0&limit=20&uid=%s" % uid
        # 种子用户uid
        # start_url = "https://www.oppo.cn/follow/default/followers.json?page=%s&limit=20&uid=%s" % (0, uid)
        # yield scrapy.Request(start_url, callback=self.serach_parsing, cb_kwargs={"uid": uid})
        start_url_list = read_top_excel()

        for start_url in start_url_list.get("oppo"):
            uid = start_url.split("-")[-2]
            yield from self.mid(uid)

    def mid(self, uid):
        url = "https://www.oppo.cn/follow/default/followers.json?page=%s&limit=20&uid=%s" % (0, uid)
        yield scrapy.Request(url, callback=self.serach_parsing, cb_kwargs={"uid": uid})

    def serach_parsing(self, rep, uid):
        fans_total = json.loads(rep.text).get("total")
        if fans_total > 0:
            pages = fans_total / 20
            if isinstance(pages, float):
                pages = int(pages) + 2
            else:
                pages = pages + 1
            for page in range(0, pages + 1):
                fans_url = "https://www.oppo.cn/follow/default/followers.json?page=%s&limit=20&uid=%s" % (
                    page, uid)
                data_url = "https://www.oppo.cn/member-%s-1" % uid
                if self.conn_redis_.sadd("oppo_url",data_url) == 1:
                    self.start = time.time()
                    yield scrapy.Request(fans_url, callback=self.fans_data, cb_kwargs={"url": data_url})
                # time.sleep(4)

    def fans_data(self, rep, url):
        item = GeneralItem()
        root_ = json.loads(rep.text)
        if root_.get("data"):
            for root1 in root_.get("data"):
                username = root1.get("username")
                uid = root1.get("uid")
                item["username"] = username
                item["url"] = url
                yield item
                end = float(time.time())
                logging.info("oppo One Spider Time : %s" % (end - self.start))
                yield from self.mid(uid)
