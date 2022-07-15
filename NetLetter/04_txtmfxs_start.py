from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


if __name__ == '__main__':
    setting = get_project_settings()
    today = datetime.now()
    setting["csv_filename"] = "04_txtmfxs.csv"
    setting["LOG_FILE"] = "../spider_log/04_txtmfxs_{}_{}_{}.log".format(today.year, today.month, today.day)
    setting["CONCURRENT_REQUESTS"] = 5
    process = CrawlerProcess(setting)
    process.crawl("04_txtmfxs")
    process.start()
