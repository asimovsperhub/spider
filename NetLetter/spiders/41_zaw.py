import json
import time

import scrapy

from ..items import GeneralItem


class Zaw(scrapy.Spider):
    name = "41_zaw"

    def start_requests(self):
        time_ = round(time.time() * 1000)
        for i in range(100000000, 170000000):
            url = "https://album.zhenai.com/api/profile/getObjectProfile.do?objectID=%d&_=%d" % (i,
                                                                                                 time_) + "&ua=h5%2F1.0.0%2F1%2F0%2F0%2F0%2F0%2F0%2F%2F0%2F0%2F48391e46-9669-4960-abf7-e0b894930614%2F0%2F0%2F1622609112&data=eyJ2IjoiSEJOTWgrMTM3Ym9qMkJQL0NaZS93Zz09Iiwib3MiOiJ3ZWIiLCJpdCI6MTQ3NiwidCI6ImxFYXVWcE5kSFVUVkRPYjIvT1hld3BQTHRkWS9vd09pbklHZWF5VkhpRUdmNm1XSHVNVGN1S3lBVTFmTUNPRHJuMHNNeTJuVnNXODdaZERpT0t2MG9BPT0ifQ%3D%3D&MmEwMD=5.OCg.KYsBsedIfJvLF_Tw9kgY.g23IZ8IyadvmulA9uCvw2a3yuR5_XKLzkI5DogIEVGu7IporUsRjhnycrggDBlVA4Y7XsYP0B50ejNgPm_bQXvmjyMVQ_FdTza5NI9JyWTIT1GE1BZ0kSRV.UQxsP6uf0bdsi3ikc_krbFcI8Q5vrXT44Y1XtzZWh4SQNW_RNoPCLkBsubYhdrhDjs_4FeS1tFDtMvxDBt6LHsEaJmf0wTWXnKqyf0gM40vMAnWxezCV7qfhp6gvd4NL6QDaKsXeOi2PW5mmAJcGkvFexqRpfyAkCKhcII_CpsVKOu"
            yield scrapy.Request(url, callback=self.parse, cb_kwargs={"uid": i})

    def parse(self, response, **kwargs):
        item = GeneralItem()
        rep = json.loads(response.text)
        if rep.get("data"):
            item["username"] = response.get("data").get("nickname")
            item["url"] = "https://album.zhenai.com/u/%d" % kwargs.get("uid")
            yield item
