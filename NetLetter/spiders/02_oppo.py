import scrapy
import time
from NetLetter.items import PostItem
from scrapy.http import TextResponse

# oppo 社区 帖子


class QuotesSpider(scrapy.Spider):
    name = "02_oppo"

    def start_requests(self):
        for i in range(1, 1000000000):
            link = f"https://i-thread.oppo.cn/thread/v9/hot/index.json?type=0&page={i}&pageSize=20&platform=android&ua=oppocommunity&modal=LIO-AN00&use_skin=false&screen_size=900x1600&os=5.1.1&color_os=0&s_version=81102&imei=fZ6NzJb8uQdFvHMQy2%2FKWJd6JM6berN50AKVE%2FRQhdY%3D&networktype=wifi&_t=1621493173007&_sign=31d24cbd815abf95f9cca2951c62030039a784ed&oaid&vaid&udid&aaid&uuid=16f78378-bcac-4145-8f02-6034aec499ca&color_os_name=null"
            yield scrapy.Request(link, callback=self.parse,  cb_kwargs={"page": str(i)})

    def parse(self, response: TextResponse, page):
        result = response.json()
        data = result.get('data')
        if data:
            for v in data:
                url = v.get('jump_url')
                if url:
                    url = url.replace('http', 'https', 1)
                    yield scrapy.Request(url, callback=self.parse2, cb_kwargs={})
                else:
                    self.log(f'not found jump_url')
        else:
            self.log(f'not found data in "{page}"')

    def parse2(self, response, **kwargs):
        author = response.css('.nickname ::text').get()
        datetime = response.css('.aid-text>:first-child::text').get()
        title = response.css('.title::text').get()
        context = '\n'.join([v.strip() for v in response.css('.content::text').getall()])
        item = PostItem(
            spider_name=self.name,
            url=response.url,
            author=author,
            datetime=datetime,
            title=title,
            context=context,
            ct=int(time.time()),
        )
        # print(context)
        yield item
