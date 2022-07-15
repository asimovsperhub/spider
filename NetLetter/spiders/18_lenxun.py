import json

import scrapy
from fake_useragent import UserAgent

from ..items import GeneralItem


class Lenxun(scrapy.Spider):
    name = "lenxun"

    def start_requests(self):
        for i in range(54461932,99999999):
            url = "http://3g.lexun.com/api/zone/Zone/Get?lxt=629a89c1fd6b1ff3sxvqcgvtsq&_r=325857&userid=%d" % i
            headers = {
                'user-agent': str(UserAgent(verify_ssl=False).random),
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                'Cookie': "route=14b2b7855093fbdbec2af7745f693c8a; _lxenablecookie=1; lxid=7fef728A-be6c-4520-b64a-28c1e46e0e81[202105181831]; b8ba918252ba18fdfa64cc48394f7e1b=7ec428d8db172360a4722f9f445e03d16bc2072033a4de7bea72d3913609792db975d88ec72408b0f26f21b4016b72724426d16b5ac293b8d0596b599d5a44de; lexun.com=lxt=629a89c1fd6b1ff3sxvqcgvtsq; 1B298C801AFF7F25BE8726E62AFCC8A0=629a89c1fd6b1ff3sxvqcgvtsq"
            }
            yield scrapy.Request(url, headers=headers, callback=self.parse, cb_kwargs={"uid": i})

    def parse(self, response, **kwargs):
        item = GeneralItem()
        info = json.loads(response.text)
        if info.get("data"):
            username = info.get("data").get("user").get("name")
            url = "http://3g.lexun.com/touch/friend/%d" % kwargs.get("uid")
            item["username"] = username
            item["url"] = url
            yield item
