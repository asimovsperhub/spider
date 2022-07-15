from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


if __name__ == '__main__':
    setting = get_project_settings()
    today = datetime.now()
    setting["LOG_FILE"] = "../spider_log/40_cjw_{}_{}_{}.log".format(today.year, today.month, today.day)
    setting["CONCURRENT_REQUESTS"] = 1
    setting["ITEM_PIPELINES"] = {
        # 'NetLetter.pipelines.PostMongoPipeline': 500,
    }
    setting['DEFAULT_REQUEST_HEADERS'] = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    process = CrawlerProcess(setting)
    process.crawl("40_cjw")
    process.start()
