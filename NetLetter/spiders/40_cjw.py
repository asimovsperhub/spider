import scrapy
import re
import time
from NetLetter.items import PostItem
from scrapy.http import TextResponse

# 财经网 帖子


class QuotesSpider(scrapy.Spider):
    name = "40_cjw"

    def start_requests(self):
        url = "https://www.yuncaijing.com/news/id_%s.html"
        # for i in range(14000000, 16000000):
        for i in range(15244603, 16000000):
            link = url % i
            print(link)
            yield scrapy.Request(link, callback=self.parse,  cb_kwargs={"id": str(i)})

    def parse(self, response: TextResponse, id):
        title = response.css('#news-title::text').get('').strip()

        if not(title):
            return

        datetime = re.search(r'发布时间:(.+)  ', response.css('#news-title+div ::text').get(''))
        datetime = datetime[1].strip() if datetime else ''

        context = '\n'.join([v.strip() for v in response.css('#news-content::text').getall()])

        item = PostItem(
            spider_name=self.name,
            url=response.url,
            author='',
            datetime=datetime,
            title=title,
            context=context,
            ct=int(time.time()),
        )
        # print(title)
        yield item
