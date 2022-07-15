from os import stat, stat_result
import scrapy
import time
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from NetLetter.items import PostItem
from scrapy.http import TextResponse, request


class A09PostGlhSpider(scrapy.Spider):
    name = '30_post_szwb'

    def start_requests(self):
        yield self.request_news()
        yield self.request_article()
        yield self.request_inst()
        yield self.request_sale()
        yield self.request_evaluating()
        yield self.request_evaluating_use()

    def _get_article_url(self, v):
        id = v.get("id")
        if id:
            q = f'/article-{id}-1.html'
        if q:
            return scrapy.Request('https://www.dgtle.com'+q, callback=self.parse_article, priority=10)

    def request_article(self, page: int = 1, empty_count=0, last_id=0):
        def parse(response: TextResponse):
            # print(f'article{page}')
            _empty_count = empty_count
            _last_id = last_id
            result = response.json()
            status = result.get('status')
            data = result.get('data')
            if status == 'success' and data:
                dataList = data.get('dataList')
                if dataList:
                    for v in dataList:
                        yield self._get_article_url(v)
                    _last_id = v.get('created_at')
                else:
                    self.log(f'get empty dataList in article "{page}"')
                    _empty_count += 1
            else:
                self.log(f'get empty data in article "{page}"')
                _empty_count += 1
            if _empty_count < 10:
                yield self.request_article(page+1, _empty_count, _last_id)

        url = f'https://www.dgtle.com/article/getList/0?page={page}&pushed=0&last_id={last_id}'
        return scrapy.Request(url, callback=parse)

    def _get_news_url(self, v):
        id = v.get("id")
        if id:
            category_id = v.get('category_id')
            type_id = v.get('type_id')
            if category_id == 388:
                q = f"/news-{id}-15.html"
            elif category_id == 387:
                q = f"/news-{id}-16.html"
            elif type_id == 5:
                pass
            else:
                q = f"/news-{id}-{type_id}.html"
        if q:
            return scrapy.Request('https://www.dgtle.com'+q, callback=self.parse_news, priority=10)

    def request_news(self, page: int = 1, empty_count=0, last_id=0):
        def parse(response: TextResponse):
            print(f'news{page}')
            _empty_count = empty_count
            _last_id = last_id
            result = response.json()
            status = result.get('status')
            data = result.get('data')
            if status == 'success' and data:
                dataList = data.get('dataList')
                if dataList:
                    for v in dataList:
                        yield self._get_news_url(v)
                    _last_id = v.get('created_at')
                else:
                    self.log(f'get empty dataList in news "{page}"')
                    _empty_count += 1
            else:
                self.log(f'get empty data in news "{page}"')
                _empty_count += 1
            if _empty_count < 10:
                yield self.request_news(page+1, _empty_count, _last_id)

        url = f'https://www.dgtle.com/news/getNewsIndexList/0?page={page}&last_id={last_id}'
        return scrapy.Request(url, callback=parse)

    def _get_inst_url(self, v):
        quoted_type = v.get("quoted_type")
        quoted_id = v.get("quoted_id")
        if quoted_type == 0:
            url = v.get('url')
            if url.startswith('/inst-'):
                return scrapy.Request('https://www.dgtle.com'+url, callback=self.parse_inst, priority=10)
            elif url.startswith('/article-'):
                return scrapy.Request('https://www.dgtle.com'+url, callback=self.parse_article, priority=10)
            elif url.startswith('/evaluating-'):
                return scrapy.Request('https://www.dgtle.com'+url, callback=self.parse_evaluating, priority=10)
            elif url.startswith('/news-'):
                return scrapy.Request('https://www.dgtle.com'+url, callback=self.parse_news, priority=10)
            elif url.startswith('/sale-'):
                return scrapy.Request('https://www.dgtle.com'+url, callback=self.parse_sale, priority=10)
        elif quoted_type == 1:
            q = "/article-{quoted_id}-1.html"
            return scrapy.Request('https://www.dgtle.com'+q, callback=self.parse_article, priority=10)
        elif quoted_type == 2:
            q = "/evaluating-{quoted_id}-1.html"
            return scrapy.Request('https://www.dgtle.com'+q, callback=self.parse_evaluating, priority=10)
        elif quoted_type == 4:
            q = "/inst-{quoted_id}-1.html"
            return scrapy.Request('https://www.dgtle.com'+q, callback=self.parse_inst, priority=10)
        elif quoted_type == 14:
            q = "/news-{quoted_id}-1.html"
            return scrapy.Request('https://www.dgtle.com'+q, callback=self.parse_news, priority=10)

    def request_inst(self, page: int = 1,  empty_count=0, last_id=0):
        def parse(response: TextResponse):
            print(f'inst{page}')
            _empty_count = empty_count
            _last_id = last_id
            result = response.json()
            status = result.get('status')
            data = result.get('data')
            if status == 'success' and data:
                dataList = data.get('dataList')
                if dataList:
                    for v in dataList:
                        yield self._get_inst_url(v)
                    _last_id = v.get('score')
                else:
                    self.log(f'get empty dataList in inst "{page}"')
                    _empty_count += 1
            else:
                self.log(f'get empty data in inst "{page}"')
                _empty_count += 1
            if _empty_count < 10:
                yield self.request_inst(page+1, _empty_count, _last_id)

        url = f'https://www.dgtle.com/feed/getHotDynamic?last_id={last_id}'
        return scrapy.Request(url, callback=parse)

    def _get_evaluating_use_url(self, v):
        id = v.get("id")
        if id:
            q = f"/evaluating-use-{id}-1.html"
            return scrapy.Request('https://www.dgtle.com'+q, callback=self.parse_evaluating_use, priority=10)

    def request_evaluating_use(self, page: int = 1,  empty_count=0, last_id=0):
        def parse(response: TextResponse):
            print(f'evaluating_use{page}')
            _empty_count = empty_count
            _last_id = last_id
            result = response.json()
            status = result.get('status')
            data = result.get('data')
            if status == 'success' and data:
                dataList = data.get('dataList')
                if dataList:
                    for v in dataList:
                        yield self._get_evaluating_use_url(v)
                    _last_id = v.get('created_at')
                else:
                    self.log(f'get empty dataList in evaluating_use "{page}"')
                    _empty_count += 1
            else:
                self.log(f'get empty data in evaluating_use "{page}"')
                _empty_count += 1
            if _empty_count < 10:
                yield self.request_evaluating_use(page+1, _empty_count, _last_id)

        url = f'https://www.dgtle.com/evaluating/getEvaluatingExperienceList/0?page={page}&last_id={last_id}'
        return scrapy.Request(url, callback=parse)

    def _get_evaluating_url(self, v):
        id = v.get("id")
        if id:
            q = f"/evaluating-{id}-1.html"
            return scrapy.Request('https://www.dgtle.com'+q, callback=self.parse_evaluating, priority=10)

    def request_evaluating(self, page: int = 1,  empty_count=0, last_id=0):
        def parse(response: TextResponse):
            print(f'evaluating{page}')
            _empty_count = empty_count
            _last_id = last_id
            result = response.json()
            status = result.get('status')
            data = result.get('data')
            if status == 'success' and data:
                dataList = data.get('dataList')
                if dataList:
                    for v in dataList:
                        yield self._get_evaluating_url(v)
                    _last_id = v.get('start_time')
                else:
                    self.log(f'get empty dataList in evaluating "{page}"')
                    _empty_count += 1
            else:
                self.log(f'get empty data in evaluating "{page}"')
                _empty_count += 1
            if _empty_count < 10:
                yield self.request_evaluating(page+1, _empty_count, _last_id)

        url = f'https://www.dgtle.com/evaluating/getEvaluatingList/0?page={page}&last_id={last_id}'
        return scrapy.Request(url, callback=parse)

    def _get_sale_url(self, v):
        id = v.get("id")
        if id:
            q = f"/sale-{id}-1.html"
            return scrapy.Request('https://www.dgtle.com'+q, callback=self.parse_sale, priority=10)

    def request_sale(self, page: int = 1,  empty_count=0, last_id=0):
        def parse(response: TextResponse):
            print(f'sale{page}')
            _empty_count = empty_count
            _last_id = last_id
            result = response.json()
            status = result.get('status')
            data = result.get('data')
            if status == 'success' and data:
                dataList = data.get('dataList')
                if dataList:
                    for v in dataList:
                        yield self._get_sale_url(v)
                    _last_id = v.get('created_at')
                else:
                    self.log(f'get empty dataList in sale "{page}"')
                    _empty_count += 1
            else:
                self.log(f'get empty data in sale "{page}"')
                _empty_count += 1
            if _empty_count < 10:
                yield self.request_sale(page+1, _empty_count, _last_id)

        url = f'https://www.dgtle.com/sale/getList/0?page={page}&last_id={last_id}'
        return scrapy.Request(url, callback=parse)

# class A09PostGlhSpider(CrawlSpider):
#     name = '30_post_szwb'
#     allowed_domains = ['www.dgtle.com']
#     start_urls = ['http://www.dgtle.com/']

#     rules = (
#         Rule(LinkExtractor(allow=r'/inst-[\w-]+\.html'), callback='parse_inst', follow=True),
#         Rule(LinkExtractor(allow=r'/evaluating-[\w-]+\.html'), callback='parse_evaluating', follow=True),
#         Rule(LinkExtractor(allow=r'/article-[\w-]+\.html'), callback='parse_article', follow=True),
#         Rule(LinkExtractor(allow=r'/news-[\w-]+\.html'), callback='parse_news', follow=True),
#         Rule(LinkExtractor(allow=r'/sale-[\w-]+\.html'), callback='parse_sale', follow=True),
#         Rule(LinkExtractor()),
#     )

    def parse_evaluating(self, response: TextResponse):
        context = '\n'.join([v.strip() for v in response.css('.left-content ::text').getall()]).strip()
        if not(context):
            return
        item = PostItem(
            spider_name=self.name,
            url=response.url,
            author='',
            datetime='',
            title=response.css('.bdDesc::text').get(),
            context=context,
            ct=int(time.time()),
        )
        return item

    def parse_evaluating_use(self, response: TextResponse):
        context = '\n'.join([v.strip() for v in response.css('#articleContent ::text').getall()]).strip()
        if not(context):
            return
        datetime = response.css('.bdDesc + div span ::text').getall()
        datetime = datetime[1].strip() if len(datetime) > 1 else ''
        item = PostItem(
            spider_name=self.name,
            url=response.url,
            author=response.css('.user-msg-2 p::text').get(),
            datetime=datetime,
            title=response.css('.bdDesc::text').get(),
            context=context,
            ct=int(time.time()),
        )
        return item

    def parse_article(self, response: TextResponse):
        context = '\n'.join([v.strip() for v in response.css('.articles-comment  ::text').getall()]).strip()
        if not(context):
            context = '\n'.join([v.strip() for v in response.css('#articleContent  ::text').getall()]).strip()
            if not(context):
                return
            return PostItem(
                spider_name=self.name,
                url=response.url,
                author=response.css('.user-msg-2 p::text').get(),
                datetime=response.css('.description time::text').get(),
                title=response.css('.title::text').get(),
                context=context,
                ct=int(time.time()),
            )

        item = PostItem(
            spider_name=self.name,
            url=response.url,
            author=response.css('.author::text').get(),
            datetime=response.css('.info time::text').get(),
            title=response.css('.title::text').get(),
            context=context,
            ct=int(time.time()),
        )
        return item

    def parse_news(self, response: TextResponse):
        context = '\n'.join([v.strip() for v in response.css('#articleContent ::text').getall()]).strip()
        if not(context):
            return
        item = PostItem(
            spider_name=self.name,
            url=response.url,
            author=response.css('.common-article-writer .user-msg p::text').get(),
            datetime=response.css('.description time::text').get(),
            title=response.css('.title::text').get(),
            context=context,
            ct=int(time.time()),
        )
        return item

    def parse_sale(self, response: TextResponse):
        context = '\n'.join([v.strip() for v in response.css('.idel_detail-left-swiper ::text').getall()]).strip()
        if not(context):
            return
        item = PostItem(
            spider_name=self.name,
            url=response.url,
            author=response.css('.idle-details-wap .idel_detail-right .idel_detail-right-1 dl h6::text').get(),
            datetime=response.css('.idle-details-wap .idel_detail-left-1 div .spot + span::text').get(),
            title=response.css('.title::text').get(),
            context=context,
            ct=int(time.time()),
        )
        return item

    def parse_inst(self, response: TextResponse):
        s = response.css('.avatar + div > span::text').getall()
        author = s[0] if len(s) > 0 else ''
        datetime = s[1] if len(s) > 1 else ''
        context = '\n'.join([v.strip() for v in response.css('.interset-content-section ::text').getall()]).strip()
        if not(context):
            return
        item = PostItem(
            spider_name=self.name,
            url=response.url,
            author=author,
            datetime=datetime,
            title='',
            context=context,
            ct=int(time.time()),
        )
        return item
