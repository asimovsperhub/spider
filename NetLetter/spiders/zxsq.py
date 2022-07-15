import json

import scrapy

from ..items import GeneralItem


class Zsxq(scrapy.Spider):
    name = "zsxq"

    def start_requests(self):
        for index in range(30):
            # https://public.zsxq.com/API/labels/groups?index=20&count=10
            url = "https://public.zsxq.com/API/labels/groups?index=%s&count=10" % (index * 10)
            yield scrapy.Request(url, callback=self.parsing)

    def parsing(self, rep):
        data = json.loads(rep.text)
        groups = data.get("resp_data").get("groups")
        # print(groups)
        for i in groups:
            group_id = i.get("group_id")
            # group_ids.append(group_id)
            group_url = "https://public.zsxq.com/groups/%s.html" % group_id

            yield scrapy.Request(group_url, callback=self.single_parsing)

    def single_parsing(self, rep):
        item = GeneralItem()
        # group_rep = requests.get(group_url, headers)
        # group_rep.encoding = 'utf-8'
        # root = rep.xpath(group_rep.text)
        topic_xpath = '//*[@id="__layout"]/div/div/div/main/div[9]/div[2]/div'
        # //*[@id="__layout"]/div/div/div/main/div[8]/div[2]/div[1]/div/div[1]/div/div[1]
        # <div class="name" data-v-5905f620></div> <div class="time" data-v-5905f620>5 小时前</div>
        for topic in rep.xpath(topic_xpath):
            username = topic.xpath('./span[1]/text()').get()
            item["username"] = username
            item["url"] = " "
            yield item

