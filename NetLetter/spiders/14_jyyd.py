import scrapy
import time
from NetLetter.items import GeneralItem
from scrapy.http import TextResponse, request


class A09PostGlhSpider(scrapy.Spider):
    name = '14_jyyd'

    def start_requests(self):
        yield self.get_category()

    def get_category(self):
        def parse(response: TextResponse):
            result = response.json()
            dataJson = result.get('dataJson')
            for c in dataJson:
                items = c.get('items')
                clazz = c.get('id')
                for v in items:
                    catId = v.get('id')
                    yield self.request(clazz, catId)

        body = "appKey=201020412&s=&%24referrer=com.chuangyue.reader.bookstore.ui.fragment.BookStoreFragment&versionCode=393&uuid=a3d31f7b-84c2-44a0-a338-af3817ea1eab&interfaceCode=206&u=&imei=863064835471733&distinct_id=bcbe5de1766d3179&channel=hyapp1006&android_id=bcbe5de1766d3179&userKey=690202c27f878fa0f86995b8bda7ef2d&sign=c7e55495d1671c23ccc9e6fe2f9b0bee&portal_type=0&os_api_level=22&versionName=2.1.0&device_id=bcbe5de1766d3179&osType=0&login_type=0&%24screen_name=com.chuangyue.reader.bookstore.ui.fragment.BookStoreFragment&sex=1&applicationId=com.ihuayue.jingyu&smid=202106011717272d22c364f6ef755c6f8e3973ae891243012480c543c68ccf"
        headers = {
            "Charset": 'UTF-8',
            'User-Agent': 'Apache-HttpClient/UNAVAILABLE (java 1.4)',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        return scrapy.Request("https://www.jingyu.com/apiConfig/getCateList", method='POST', headers=headers, body=body, callback=parse)

    def request(self, clazz, catId, page: int = 1,  empty_count=0):
        def parse(response: TextResponse):
            print(f'clazz={clazz} catId={catId} page={page}')
            _empty_count = empty_count
            result = response.json()
            status = result.get('status')
            data = result.get('dataJson')
            if status == 0 and data:
                dataList = data.get('list')
                if dataList:
                    for v in dataList:
                        username = v.get('authorName')
                        id = v.get('id')
                        if username and id:
                            yield GeneralItem(
                                url=f'app://{self.name}/getCategoryDetail/{id}',
                                username=username,
                            )
                else:
                    self.log(f'get empty dataList in "{page}"')
                    _empty_count += 1
            else:
                self.log(f'get empty data in "{page}"')
                _empty_count += 1
            if _empty_count < 100:
                yield self.request(clazz, catId, page+1,  _empty_count)

        body = f"appKey=201020412&s=&%24referrer=com.chuangyue.reader.discover.ui.activity.DiscoverCategoryActivity&versionCode=393&uuid=a3d31f7b-84c2-44a0-a338-af3817ea1eab&catId={catId}&interfaceCode=206&u=&imei=863064835471733&distinct_id=bcbe5de1766d3179&currentPage={page}&channel=hyapp1006&android_id=bcbe5de1766d3179&userKey=690202c27f878fa0f86995b8bda7ef2d&order=1&sign=215c2d3994e0aa85b702103b06af4513&clazz={clazz}&pageSize=10&portal_type=0&os_api_level=22&versionName=2.1.0&device_id=bcbe5de1766d3179&osType=0&login_type=0&%24screen_name=com.chuangyue.reader.discover.ui.activity.CategoryBookActivity&sex=1&applicationId=com.ihuayue.jingyu&smid=202106011717272d22c364f6ef755c6f8e3973ae891243012480c543c68ccf"
        headers = {
            "Charset": 'UTF-8',
            'User-Agent': 'Apache-HttpClient/UNAVAILABLE (java 1.4)',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        return scrapy.Request("https://www.jingyu.com/api/getCategoryDetail", headers=headers, method='POST', body=body, callback=parse)
