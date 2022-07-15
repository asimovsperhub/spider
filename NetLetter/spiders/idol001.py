import json
import logging
import time

import scrapy

from ..items import GeneralItem


class AiDouSpider(scrapy.Spider):
    name = "idol001"

    def start_requests(self):
        channl_url = "http://static.idol001.com/userquanzi/type_list/main.json"
        yield scrapy.Request(channl_url, callback=self.channl_parsing)

    def channl_parsing(self, rep):
        channl_list = json.loads(rep.text).get("list")
        for channl in channl_list:
            quanzi_url = "http://static.idol001.com/userquanzi/type_list/%s.json" % channl.get("typeid")
            yield scrapy.Request(quanzi_url, callback=self.quanzi_parsing)

    def quanzi_parsing(self, rep):

        quanzi_list = json.loads(rep.text).get("list")
        for quanzi in quanzi_list:
            for page in range(10000):
                article_url = "http://data.idol001.com/api_moblie_idol_userquanzi.php?action=get_message_list&order=recom_time&app_platform=android&version=250&qzid=%s&count=10&page=%s" % (
                    quanzi.get("_id"), page)
                yield scrapy.Request(article_url, callback=self.article_parsing,
                                     cb_kwargs={'quanzi_id': quanzi.get("_id")})

    def article_parsing(self, rep, quanzi_id):
        if len(json.loads(rep.text).get("list")) > 0:
            article_list = json.loads(rep.text).get("list")
            for article in article_list:
                article_details_url = "https://data.idol001.com/api_moblie_idol_userquanzi.php?action=get_message_comment_list&messageid=%s&qzid=%s&order=time&page=1&version=250&app_platform=android" % (
                    article.get("_id"), quanzi_id)
            yield scrapy.Request(article_details_url, callback=self.article_details_parsing)

    def article_details_parsing(self, rep):
        article_details_list = json.loads(rep.text).get("list")
        for article_details in article_details_list:
            user_info_url = "http://data.idol001.com/api_moblie_idol.php?action=get_userinfo_detail&userid=%s" % article_details.get(
                "userid")
            self.start = float(time.time())
            yield scrapy.Request(user_info_url, callback=self.user_info_parsing, cb_kwargs={"url": user_info_url})

    def user_info_parsing(self, rep, url):
        item = GeneralItem()
        rep.encode = 'utf8'
        item["username"] = json.loads(rep.text).get("nickname")
        item["url"] = url
        yield item
        end = float(time.time())
        logging.info("idol001 One Spider Time : %s" % (end - self.start))
