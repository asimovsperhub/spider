from typing import List
import scrapy
import re
import time
from NetLetter.items import PostItem
from scrapy.http import TextResponse

# 酷安 帖子


class QuotesSpider(scrapy.Spider):
    name = "17_post_kuan"

    def __init__(self):
        self.headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; LIO-AN00 Build/LIO-AN00) (#Build; Android; LIO-AN00; LIO-AN00-user 5.1.1 LIO-AN00 500210421 release-keys; 5.1.1) +CoolMarket/11.2-2105201-universal",
            "X-Requested-With": "XMLHttpRequest",
            "X-Sdk-Int": "22",
            "X-Sdk-Locale": "zh-CN",
            "X-App-Id": "com.coolapk.market",
            "X-App-Token": "v2JDJ5JDEwJE1UWXlNVFUyTXpNM09RL2I4YTk0YXVMSzN6d2pMSFZnWXlOc1pWeWt0QVN3a3VnRmc3Tmph",
            "X-App-Version": "11.2",
            "X-App-Code": "2105201",
            "X-Api-Version": "11",
            "X-App-Device": "wGb15GI7MXeltWLlNXYlxWZyBSMyQDMxIDMwUDIwAjTB1yTJxEIx4SMuUDIyV2c11CMw4UQt8USMByOwAjTB1yTJxEI7QWavJHZuFEI7kURXFUVIByO2MkOBFjOENkO3IjOwAjO4ADI7AyOgsTO3EzMkZjN3ETZkVTZiNmY",
            "X-Dark-Mode": "0",
            "X-App-Channel": "coolapk",
            "X-App-Mode": "universal",
        }

    def start_requests(self):
        yield self.request_1()
        yield self.request_2()
        yield self.request_3()
        yield self.request_4()

        # # 话题
        # 'https://api.coolapk.com/v6/page/dataList?url=V9_HOME_TAB_TOPIC&title=%E8%AF%9D%E9%A2%98&page=1'

    def request_1(self, page=1, empty_data_count=0):
        def parse(response: TextResponse, page: int):
            print(f'首页{page}')
            _count = empty_data_count
            result = response.json()
            data = result.get('data')
            if data:
                for v in data:
                    yield self.do_feed(v)
            else:
                self.log(f'get empty data in 首页 "{page}"')
                _count += 1

            if _count < 10:
                yield self.request_1(page+1, _count)

        link = f"https://api.coolapk.com/v6/main/indexV8?page={page}&firstLaunch=0&installTime=1621562750702"
        return scrapy.Request(link, headers=self.headers, callback=parse, cb_kwargs={'page': page})

    def request_2(self, page=1, empty_data_count=0):
        def parse(response: TextResponse, page: int):
            print(f'热榜{page}')
            _count = empty_data_count
            result = response.json()
            data = result.get('data')
            if data:
                for v in data:
                    yield self.do_feed(v)
            else:
                self.log(f'get empty data in 热榜 "{page}"')
                _count += 1

            if _count < 10:
                yield self.request_2(page+1, _count)

        link = f'https://api.coolapk.com/v6/page/dataList?url=V9_HOME_TAB_RANKING&title=%E7%83%AD%E6%A6%9C&page={page}'
        return scrapy.Request(link, headers=self.headers, callback=parse, cb_kwargs={'page': page})

    def request_3(self, page=1, empty_data_count=0):
        def parse(response: TextResponse, page: int):
            print(f'快讯{page}')
            _count = empty_data_count
            result = response.json()
            data = result.get('data')
            if data:
                for v in data:
                    yield self.do_feed(v)
            else:
                self.log(f'get empty data in 快讯 "{page}"')
                _count += 1

            if _count < 10:
                yield self.request_3(page+1, _count)

        link = f'https://api.coolapk.com/v6/page/dataList?url=V11_HOME_TAB_NEWS&title=%E5%BF%AB%E8%AE%AF&page={page}'
        return scrapy.Request(link, headers=self.headers, callback=parse, cb_kwargs={'page': page})

    def request_4(self, page=1, empty_data_count=0):
        def parse(response: TextResponse, page: int):
            print(f'闲聊{page}')
            _count = empty_data_count
            result = response.json()
            data = result.get('data')
            if data:
                for v in data:
                    yield self.do_feed(v)
            else:
                self.log(f'get empty data in 闲聊 "{page}"')
                _count += 1

            if _count < 10:
                yield self.request_4(page+1, _count)

        link = f'https://api.coolapk.com/v6/page/dataList?url=V8_HUODONG_XIANLIAO_20210514&title=%E9%97%B2%E8%81%8A&page={page}'
        return scrapy.Request(link, headers=self.headers, callback=parse, cb_kwargs={'page': page})

    def do_feed(self, v):
        def parse_detail(response: TextResponse, url: str):
            print(url)
            result = response.json()
            data = result.get('data')
            if data:
                author = data.get('userInfo')
                author = author.get('username') if author else ''
                datetime = data.get('lastupdate')
                title = data.get('ttitle')
                if not(title):
                    title = data.get('title')
                context = data.get('message')
                item = PostItem(
                    spider_name=self.name,
                    url=f'app://{self.name}{url}',
                    author=author,
                    datetime=datetime,
                    title=title,
                    context=context,
                    ct=int(time.time()),
                )
                yield item
            else:
                self.log(f'get empty data in detail "{url}"')

        url = v.get('url')
        id = v.get('entityId')
        if id and url and url.startswith('/feed/'):
            link = f'https://api.coolapk.com/v6/feed/detail?id={id}'
            return scrapy.Request(link, headers=self.headers, callback=parse_detail, priority=10, cb_kwargs={'url': url})
