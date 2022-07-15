import scrapy
import time
from NetLetter.items import GeneralItem
from scrapy.http import TextResponse, request


class A09PostGlhSpider(scrapy.Spider):
    name = '04_txtmfxs'

    def start_requests(self):
        # yield self.request('现代修真')
        yield from self.get_category()

    def get_category(self):
        words = ["现代修真", "都市纵横", "都市异能", "娱乐明星", "校园生活", " 职场商战", "东方玄幻", "西方魔幻", "异界争霸", "洪荒神话", "传统武侠", "古典仙侠", "历史传记", "架空穿越", "峥嵘岁月",
                 "谍战特工", "未来世界", "科技争霸", "古武机甲", "末世进化", "时空穿梭", "推理悬念", "灵异怪谈", "风水秘术", "探险异闻", "虚拟网游", "电子竞技", "体育竞技", "原生幻想", "轻松搞笑"]
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

        url = f'http://api.ydnovel.net/api/bookapp/searchdzh.m?word={word}&type=2&page_id={page}&count=20&sort_type=0&subclass=0&datasource=0&showj=1&wc=0&catalog=0&bookStatus=0&cid=eef_easou_book&version=002&os=android&udid=FE622924735D7573DC22F8E6CC2232CF&appverion=1003&ch=blf1421_14412_001&session_id=&lastClock=0&dzh=1&scp=0&appid=40002&utype=0&rtype=3&pushid=100d855909966473fe0&ptype=5&gender=0&userInitPay=0&birt=0&userNewMedia=0&instime=1622603206329'
        return scrapy.Request(url, callback=parse)
