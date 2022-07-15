import scrapy
import time
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from NetLetter.items import PostItem
from scrapy.http import TextResponse


class A09PostGlhSpider(CrawlSpider):
    name = '09_post_glh'
    allowed_domains = ['www.gelonghui.com']
    start_urls = ['http://www.gelonghui.com/']

    rules = (
        Rule(LinkExtractor(allow=r'/p/\d+'), callback='parse_item', follow=True),
        Rule(LinkExtractor()),
    )

    def parse_item(self, response: TextResponse):
        item = PostItem(
            spider_name=self.name,
            url=response.url,
            author=response.css('.info .nick ::text').get('').strip(),
            datetime=response.css('.article-info .date ::text').get('').strip(),
            title=response.css('.article-title::text').get('').strip(),
            context='\n'.join([v.strip() for v in response.css('article ::text').getall()]),
            ct=int(time.time()),
        )
        return item
