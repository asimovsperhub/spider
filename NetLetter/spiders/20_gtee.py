import scrapy

from ..items import GeneralItem


class Gtee(scrapy.Spider):
    name = "20_gtee"

    def __init__(self):
        self.cache = set()

    def start_requests(self):
        url = "https://gitee.com/explore/all?page=%d"

        for i in range(1, 101):
            yield scrapy.Request(url % i, callback=self.parse)

    def parse(self, response, **kwargs):
        item_list = response.xpath('//*[@class="ui relaxed divided items explore-repo__list"]/div')
        for item in item_list:
            item_url = item.xpath('./div/div[1]/div[1]/h3/a/@href').get()
            art_url = "https://gitee.com" + item_url
            yield scrapy.Request(art_url, callback=self._parse)

    def _parse(self, response, **kwargs):
        master_url = response.xpath('//*[@id="contributor"]/div[1]/a/@href').get()
        url = "https://gitee.com" + master_url
        yield scrapy.Request(url, callback=self.__parse)

    def __parse(self, response, **kwargs):
        masters = response.xpath('//*[@class="ui horizontal relaxed list"]/div')
        for master in masters:
            user_url = master.xpath('./div/div/a/@href').get()
            if user_url:
                user_index = "https://gitee.com" + user_url
                if "mailto" in user_url:
                    user_index = "https://gitee.com/" + user_url.split(":")[-1]
                yield scrapy.Request(user_index, callback=self.parseuser)

    def parseuser(self, response, **kwargs):
        if response.url not in self.cache:
            if response.status > 400:
                return
            item = GeneralItem()
            username = response.xpath('//*[@id="rc-users__container"]/div[1]/div[1]/div[2]/h2/span/text()').get()
            if username:
                item["username"] = username
                item["url"] = response.url
                self.cache.add(response.url)
                fansurl = response.url + "/followers"
                yield item
                yield scrapy.Request(fansurl, callback=self.fans)

    def fans(self, response, **kwargs):
        fans_count = response.xpath(
            '//*[@id="rc-users__container"]/div[2]/div/div/div/div/div[1]/div[1]/strong/text()').get()
        if fans_count:
            count = int(fans_count.split("(")[-1].split(")")[0])

            if count > 0:
                if count < 48:
                    pages = 1
                else:
                    pages = int(count / 48) + 1
                for page in range(1, pages + 1):
                    page_url = response.url + "?page=%d" % page
                    yield scrapy.Request(page_url, callback=self.fans_list)

    def fans_list(self, response, **kwargs):

        user_list = response.xpath('//*[@id="target-list"]/div[1]/div')
        for user in user_list:
            user_url = user.xpath('./div/div[2]/strong/a/@href').get()
            if user_url:
                user_index = "https://gitee.com" + user_url
                if "mailto" in user_url:
                    user_index = "https://gitee.com/" + user_url.split(":")[-1]
                yield scrapy.Request(user_index, callback=self.parseuser)
