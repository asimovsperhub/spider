from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


if __name__ == '__main__':
    setting = get_project_settings()
    today = datetime.now()
    setting["csv_filename"] = "35_xgzb.csv"
    setting["LOG_FILE"] = "../spider_log/35_xgzb_{}_{}_{}.log".format(today.year, today.month, today.day)
    setting["CONCURRENT_REQUESTS"] = 5
    process = CrawlerProcess(setting)
    process.crawl("35_xgzb")
    process.start()
