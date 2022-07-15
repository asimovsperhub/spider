import re

import scrapy

from ..items import GeneralItem


class Bdb(scrapy.Spider):
    name = "6_bendibao"

    def __init__(self):
        self.szbendibao = {}
        self.level_2_xpath = {
            "新闻": ['//*[@id="channelNav"]/li', './/@href'],
            "休闲": ['//*[@id="topnav"]/ul/li', './/@href'],
            "旅游": ['//*[@id="header"]/div/ul/li', './/@href'],
            "免费": ['/html/body/div[3]/div/div[2]/p[2]/a', './/@href'],
            # //*[@id="tabnav"]
            "交通": ['//*[@id="subnav"]/ul/li', './/@href'],
            "教育": ['//*[@id="subnav"]/ul/li', './/@href']
        }

    def start_requests(self):

        urls = ["http://sz.bendibao.com/"]
        for url in urls:
            yield scrapy.Request(url, callback=self.level_1_navigation)

    def level_1_navigation(self, rep):
        navigation = rep.xpath('//*[@id="main-wrap"]/div[2]/div')

        for type_ in navigation:
            text = type_.xpath('./ul[1]/li[1]//text()').get()
            href = type_.xpath('./ul[1]/li[1]//@href').get()
            text1 = type_.xpath('./ul[2]/li[1]//text()').get()
            href1 = type_.xpath('./ul[2]/li[1]//@href').get()
            self.szbendibao.setdefault(href, text)
            self.szbendibao.setdefault(href1, text1)
        for url_ in self.szbendibao.keys():
            if "http" in url_:
                yield scrapy.Request(url_, callback=self.level_2_navigation)

    def level_2_navigation(self, rep):
        level_2_list = []
        if self.szbendibao.get(rep.url):
            url_type = self.szbendibao.get(rep.url)
            navigation = rep.xpath(self.level_2_xpath.get(url_type)[0])
            for type_ in navigation:
                # text = type.xpath('.//text()').get()
                href = type_.xpath(self.level_2_xpath.get(url_type)[1]).get()
                if href:
                    if 'http' not in href:
                        href = "http://ly.sz.bendibao.com" + href
                    level_2_list.append(href)
        if "jt" in rep.url:
            for t in rep.xpath('//*[@id="tabnav"]/ul/li'):
                h = t.xpath('.//@href')
                if h:
                    level_2_list.append(h)
        for level_2 in level_2_list:
            yield scrapy.Request(level_2, callback=self.level_3_navi)

    def level_3_navi(self, rep):
        if "news" or "jt" or "edu" in rep.url:
            if rep.xpath('//*[@id="AspNetPager1"]/ul/li[21]/a/text()').get() == "末页":
                offset = rep.xpath('//*[@id="AspNetPager1"]/ul/li[21]/a/@href').get()
                # offset = rep.xpath('//*[@id="AspNetPager1"]/ul/li[21]/a/@href')
                off = re.search(r"\d+", offset).group(0)
                for x in range(1, int(off) + 1):
                    off_limit = rep.url + "list%d.htm" % x
                    yield scrapy.Request(off_limit, callback=self.level_4_navi)
            else:
                url1 = rep.url + "list1.htm"
                yield scrapy.Request(url1, callback=self.level_4_navi)
        if "tour" in rep.url:
            if rep.xpath('//*[@id="ctl00_LastPage"]//text()').get() == "最后一页":
                # //*[@id="ctl00_LastPage"]
                offset = rep.xpath('//*[@id="ctl00_LastPage"]//@href').get()
                off = offset.split("_")[-1].split(".")[0]
                for x in range(1, int(off) + 1):
                    off_limit = rep.url.split(".html")[0] + "_%d.html" % x
                    yield scrapy.Request(off_limit, callback=self.level_4_navi)
            else:
                url1 = rep.url.split(".html")[0] + "_%d.html" % 1
                yield scrapy.Request(url1, callback=self.level_4_navi)
        # if 'edu' in rep.url:
        #     # //*[@id="AspNetPager1"]/ul/li[21]/a
        #     pass

    def level_4_navi(self, rep):
        if "news" or "jt" or "edu" in rep.url:
            # //*[@id="listNewsTimeLy"]
            child = rep.xpath('//*[@id="listNewsTimeLy"]/li')
            for ch in child:
                child_url = ch.xpath('./div/h3/a/@href').get()
                if child_url:
                    yield scrapy.Request(child_url, callback=self.parse)
        if "tour" in rep.url:
            # /html/body/div[5]/div[1]/div[2]
            child = rep.xpath('/html/body/div[5]/div[1]/div[2]/div')
            for ch in child:
                child_url = ch.xpath('./dl/dt/a/@href').get()
                if child_url:
                    yield scrapy.Request(child_url, callback=self.parse)

    def parse(self, response, **kwargs):
        item = GeneralItem()
        # print(response.url)
        # content = re.search(r"[^\x00-\xff]", response.xpath('//*[@id="bo"]').get())
        # re.S == re.DOTALL
        content = re.compile(r'<[^>]+>', re.S).sub(' ', response.xpath('//*[@id="bo"]').get())
        item["url"] = response.url
        item["username"] = content
        yield item
