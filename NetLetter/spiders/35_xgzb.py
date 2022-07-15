import scrapy
import time
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from NetLetter.items import GeneralItem
from scrapy.http import TextResponse


class A09PostGlhSpider(CrawlSpider):
    name = '35_xgzb'
    allowed_domains = ['www.tuho.tv']
    start_urls = ['https://www.tuho.tv/']

    rules = (
        Rule(LinkExtractor(allow=r'/\d+'), callback='parse_item', follow=True),
        Rule(LinkExtractor(deny=r'/user/logout\b')),
    )

    def parse_item(self, response: TextResponse):
        username = response.css('.vm_desc_nickname::text').get('').strip()
        if username:
            return GeneralItem(
                url=response.url,
                username=username,
            )

    def start_requests(self):
        yield self.request_getroom()
        yield from super().start_requests()

    def request_getroom(self, page: int = 1,  empty_count=0):
        def parse(response: TextResponse):
            print(f'page={page}')
            _empty_count = empty_count
            result = response.json()
            data = result.get('data')
            errno = result.get('errno')
            if errno == 0 and data:
                data = data.get('rooms')
            if not(data):
                self.log(f'get empty data in "{page}"')
                _empty_count += 1
            else:
                for v in data:
                    username = v.get('nickname')
                    id = v.get('mid')
                    if username and id:
                        yield GeneralItem(
                            url=f'https://www.tuho.tv/{id}',
                            username=username,
                        )
            if _empty_count < 10:
                yield self.request_getroom(page+1,  _empty_count)

        return scrapy.FormRequest('https://www.tuho.tv/indexV4/getRoomInfo', formdata={'page': str(page)}, callback=parse)
