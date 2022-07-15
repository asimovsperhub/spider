from typing import List
import scrapy
import re
import time
from NetLetter.items import PostItem
from scrapy.http import TextResponse
from scrapy.linkextractors import LinkExtractor

# 红歌会 帖子


class Link:
    def __init__(self, url: str, depth: int) -> None:
        self.url = url
        self.depth = depth


class QuotesSpider(scrapy.Spider):
    name = "45_hgh"

    MAX_DEPTH = 2

    def __init__(self):
        self.linkExtractor = LinkExtractor(allow_domains='www.szhgh.com')
        self.requestedCache = set()

    def start_requests(self):
        yield self.request(Link('http://www.szhgh.com', 0))

    def request(self, link: Link):
        if link.url in self.requestedCache:
            return
        self.requestedCache.add(link.url)
        print('request', link.depth, link.url)
        return scrapy.Request(link.url, callback=self.parse, cb_kwargs={'link': link})

    def parse(self, response: TextResponse, **kwargs):
        yield from self.check_article(response, **kwargs)

        yield from self.find_all_link(response, **kwargs)

    def find_all_link(self, response: TextResponse, link: Link):
        # break while max depth
        if link.depth >= self.MAX_DEPTH:
            return

        depth = link.depth + 1
        # filter 去重 校验 http://www.szhgh.com/
        links = self.linkExtractor.extract_links(response)
        for v in links:
            yield self.request(Link(v.url, depth))

    def check_article(self, response: TextResponse, link: Link):
        if not(re.search(r'/Article/([\w-]+/){1,5}\d+\.html\b', link.url)):
            return

        line1 = response.css('.info_text.line1')

        author = re.search(r'作者：(.+)', ''.join(line1.css('::text').getall()))
        author = author[1].strip() if author else ''

        # line1.css('a').css('::attr(href)').get()
        # line1.css('a').css('::text').get()
        # source_link =
        # source_text =

        datetime = re.search(r'\d{4}-\d{2}-\d{2} +\d{2}:\d{2}:\d{2}', line1.css('::text').get())
        datetime = datetime[0] if datetime else ''

        title = response.css('.article_text h1').css('::text').get()

        context = '\n'.join([v.strip() for v in response.css('.article_text .newstext > p,h1,h2,h3,h4,h5').css('::text').getall()])

        # print(item['url'], item['title'])
        item = PostItem(
            spider_name=self.name,
            url=link.url,
            author=author,
            datetime=datetime,
            title=title,
            context=context,
            ct=int(time.time()),
        )
        yield item
