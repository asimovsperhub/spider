from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


if __name__ == '__main__':
    setting = get_project_settings()
    today = datetime.now()
    setting["LOG_FILE"] = "../spider_log/30_post_szwb_{}_{}_{}.log".format(today.year, today.month, today.day)
    setting["CONCURRENT_REQUESTS"] = 16
    setting["ITEM_PIPELINES"] = {
        'NetLetter.pipelines.PostMongoPipeline': 500,
    }
    process = CrawlerProcess(setting)
    process.crawl("30_post_szwb")
    process.start()
