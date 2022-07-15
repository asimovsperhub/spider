from typing import List
import scrapy
import re
import time
from NetLetter.items import PostItem
from scrapy.http import TextResponse
from scrapy.linkextractors import LinkExtractor


# 乐讯 帖子


class Link:
    def __init__(self, url: str, depth: int) -> None:
        self.url = url
        self.depth = depth


class QuotesSpider(scrapy.Spider):
    name = "18_post_lenxun"

    MAX_DEPTH = 20

    def __init__(self):
        self.linkExtractor = LinkExtractor(allow_domains=('lexun.com', 'lexun.net'))
        self.requestedCache = set()

    def start_requests(self):
        yield self.request(Link('http://3g.lexun.com', 0))

    def request(self, link: Link):
        if link.url in self.requestedCache:
            return
        self.requestedCache.add(link.url)
        # print('request', link.depth, link.url)
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
        if re.search(r'/touch/detailnew\.\w+', link.url):
            author = ''.join(response.css('.invitation_personal h2 a ::text').getall()).strip()
            datetime = ''.join(response.css('.invitation_topnum .fl ::text').getall()).strip()
            title = ''.join(response.css('.articleTitle ::text').getall()).strip()
            context = '\n'.join(response.css('.tie_detail .invitation_personal_text::text').getall()).strip()
        elif re.search(r'/touch/vdetailnew\.\w+', link.url):
            author = response.css('.dd_title::text').get()
            datetime = response.css('.dd_txt ::text').get()
            title = response.css('.mus_cont_dl + p ::text').get()
            context = '\n'.join(response.css('.invitation_personal_text::text').getall()).strip()
        elif re.search(r'/channel/detail\b', link.url):
            id = re.search(r'\bid=(\w+)', link.url)[1]
            lxt = re.search(r'\blxt=(\w+)', link.url)[1]
            _r = re.search(r'\b_r=(\w+)', link.url)[1]
            body = dict(p='1', id=id, order='3')

            def callback(response: TextResponse):
                result = response.json()
                # print(result)
                detail = result.get('detail')
                if detail:
                    item = PostItem(
                        spider_name=self.name,
                        url=link.url,
                        author=detail['user']['nick'],
                        datetime=detail['addTime'],
                        title=detail['title'],
                        context=detail['content'],
                        ct=int(time.time()),
                    )
                    print(item['url'], item['title'])
                    yield item

            yield scrapy.FormRequest(f'http://capi.lexun.com/newbbs/main/detail.aspx?lxt={lxt}&_r={_r}', formdata=body,
                                     priority=100, callback=callback)
            return
        else:
            return

        item = PostItem(
            spider_name=self.name,
            url=link.url,
            author=author,
            datetime=datetime,
            title=title,
            context=context,
            ct=int(time.time()),
        )
        # print(item['url'], item['title'])
        yield item
