import scrapy
import time
from NetLetter.items import GeneralItem
from scrapy.http import TextResponse, request


class A09PostGlhSpider(scrapy.Spider):
    name = '05_akxsdq'

    def start_requests(self):
        # yield self.request('现代言情')
        yield from self.get_category()

    def get_category(self):
        words = ["玄幻奇幻", "武侠仙侠", "科幻小说", "游戏竞技", "现代都市", "历史军事", "灵异悬疑", "宅小说", "现代言情", "古代言情", "幻想言情", "浪漫青春", "短篇", "经典名著", "其他出版", "现代文学"]
        for v in words:
            yield self.request(v)

    def request(self, word, page: int = 1,  empty_count=0):
        def parse(response: TextResponse):
            print(f'word={word} page={page}')
            _empty_count = empty_count
            result = response.json()
            data = result.get('all_book_items')
            if data:
                for v in data:
                    username = v.get('author')
                    id = v.get('nid')
                    if username and id:
                        yield GeneralItem(
                            url=f'app://{self.name}/bookSummary/{id}',
                            username=username,
                        )
            else:
                self.log(f'get empty data in "{page}"')
                _empty_count += 1
            if _empty_count < 10:
                yield self.request(word, page+1,  _empty_count)

        url = f'http://api.wejuan.cn/api/bookapp/searchdzh.m?word={word}&type=2&page_id={page}&count=20&sort_type=0&subclass=0&datasource=0&showj=1&wc=0&catalog=0&bookStatus=0&cid=eef_easou_book&version=002&os=android&udid=8DB204EE62AA712C27398A215C40D36C&appverion=1008&ch=blf1418_10928_001&session_id=&lastClock=0&dzh=1&scp=0&appid=20002&utype=0&rtype=3&pushid=1507bfd3f71414f4883&ptype=5&gender=1&userInitPay=3&birt=0&instime=1622600122428'
        return scrapy.Request(url, callback=parse)
