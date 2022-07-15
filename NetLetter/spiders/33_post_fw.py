import scrapy
import time
from NetLetter.items import PostItem
from scrapy.http import TextResponse
from NetLetter.spiders.wfdata import wfGetHeaders


class A09PostGlhSpider(scrapy.Spider):
    name = '33_post_fw'

    def start_requests(self):
        HOST = "https://api.wfdata.club"
        PATH = "/v1/thread/%s"
        # for post_id in range(13403368, 13403370):
        # for post_id in range(10000000, 10000010):
        for post_id in range(10000000, 20000000):
            path = PATH % post_id
            headers = wfGetHeaders(path)

            link = HOST + path
            yield scrapy.Request(url=link, headers=headers, callback=self.parse_item, cb_kwargs={"post_id": post_id})

    def parse_item(self, response: TextResponse, post_id: int):
        result = response.json()
        status = result.get('status')
        data = result.get('data')
        if data and status and int(status.get('code', 1)) == 0:
            thread = data.get('thread')
            if not(thread):
                self.log(f'get "{post_id}" error "no thread"')
                return
            item = PostItem(
                spider_name=self.name,
                url=f'https://www.feng.com/post/{post_id}',
                author=thread.get('authorName'),
                datetime=thread.get('updateTime'),
                title=thread.get('subject'),
                context=thread.get('message'),
                ct=int(time.time()),
            )
            return item
        else:
            errmsg = status.get('message') if status else '[empty response]'
            self.log(f'get "{post_id}" error: "{errmsg}"')
