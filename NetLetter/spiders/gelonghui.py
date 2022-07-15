# 用戶接口

# https://www.gelonghui.com/api/friendships/followers?userId=5273&page=1&count=12

# https://www.gelonghui.com/api/friendships/followers?userId=410884&page=2&count=12
import json
import logging
import time

import scrapy

from ..items import GeneralItem
from ..mongo_ import MongoL, RedisL


class GLHSpider(scrapy.Spider):
    name = "gelonghui"

    def __init__(self):
        mongo = MongoL()
        _, self.mongo_col = mongo.mongo_col()
        conn_ = RedisL()
        self.conn_redis_ = conn_.conn_redis()

    def start_requests(self):
        start_url_list = ['https://www.gelonghui.com/user/165134', 'https://www.gelonghui.com/user/107556',
                          'https://www.gelonghui.com/user/259739', 'https://www.gelonghui.com/user/126309',
                          'https://www.gelonghui.com/user/117396', 'https://www.gelonghui.com/user/107638',
                          'https://www.gelonghui.com/user/165170', 'https://www.gelonghui.com/user/324261',
                          'https://www.gelonghui.com/user/127827', 'https://www.gelonghui.com/user/10783',
                          'https://www.gelonghui.com/user/117425', 'https://www.gelonghui.com/user/443027',
                          'https://www.gelonghui.com/user/293186', 'https://www.gelonghui.com/user/107609',
                          'https://www.gelonghui.com/user/117454', 'https://www.gelonghui.com/user/293233',
                          'https://www.gelonghui.com/user/165234', 'https://www.gelonghui.com/user/107640',
                          'https://www.gelonghui.com/user/107592', 'https://www.gelonghui.com/user/293227',
                          'https://www.gelonghui.com/user/127878', 'https://www.gelonghui.com/user/293225',
                          'https://www.gelonghui.com/user/107596', 'https://www.gelonghui.com/user/225461',
                          'https://www.gelonghui.com/user/107562', 'https://www.gelonghui.com/user/126200',
                          'https://www.gelonghui.com/user/7495', 'https://www.gelonghui.com/user/107571',
                          'https://www.gelonghui.com/user/117434', 'https://www.gelonghui.com/user/117436',
                          'https://www.gelonghui.com/user/293252', 'https://www.gelonghui.com/user/127817',
                          'https://www.gelonghui.com/user/293228', 'https://www.gelonghui.com/user/359387',
                          'https://www.gelonghui.com/user/127885', 'https://www.gelonghui.com/user/117398',
                          'https://www.gelonghui.com/user/165166', 'https://www.gelonghui.com/user/117438',
                          'https://www.gelonghui.com/user/460158', 'https://www.gelonghui.com/user/14567',
                          'https://www.gelonghui.com/user/107600', 'https://www.gelonghui.com/user/107569',
                          'https://www.gelonghui.com/user/293009', 'https://www.gelonghui.com/user/418437',
                          'https://www.gelonghui.com/user/293188', 'https://www.gelonghui.com/user/117405',
                          'https://www.gelonghui.com/user/107591', 'https://www.gelonghui.com/user/107581']

        for start_url in start_url_list:
            yield from self.mid(start_url)

    def mid(self, url):
        if self.conn_redis_.sadd("gelonghui_url", url) == 1:
            user_id = url.split("/")[-1]
            fans_url = "https://www.gelonghui.com/api/friendships/followers?userId=%s&page=1&count=12" % user_id
            yield scrapy.Request(fans_url, callback=self.parsing, cb_kwargs={"user_id": user_id})

    def parsing(self, rep, user_id):
        data = json.loads(rep.text)
        fans_count = data.get("totalCount")
        if fans_count > 0:
            is_int = fans_count / 12
            if isinstance(is_int, float):
                pages = int(is_int) + 2
            else:
                pages = is_int
            # page 0 = 1 content
            for page in range(1, pages):
                url = "https://www.gelonghui.com/api/friendships/followers?userId=%s&page=%s&count=12" % (user_id, page)
                self.start = time.time()
                yield scrapy.Request(url, callback=self.fansparsing)

    def fansparsing(self, rep):
        item = GeneralItem()
        user_info = json.loads(rep.text).get("result")
        for user in user_info:
            user_id = user.get("userId")
            username = user.get("nickname")
            url = "https://www.gelonghui.com/user/%s" % user_id
            item["username"] = username
            item["url"] = url
            yield item
            end = float(time.time())
            logging.info("DGTLE One Spider Time : %s" % (end - self.start))
            yield from self.mid(url)
