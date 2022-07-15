from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


if __name__ == '__main__':
    setting = get_project_settings()
    today = datetime.now()
    setting["csv_filename"] = "14_jyyd.csv"
    setting["LOG_FILE"] = "../spider_log/14_jyyd_{}_{}_{}.log".format(today.year, today.month, today.day)
    setting["CONCURRENT_REQUESTS"] = 10
    # setting["ITEM_PIPELINES"] = {}
    process = CrawlerProcess(setting)
    process.crawl("14_jyyd")
    process.start()
