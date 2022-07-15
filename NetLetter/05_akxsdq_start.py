from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


if __name__ == '__main__':
    setting = get_project_settings()
    today = datetime.now()
    setting["csv_filename"] = "05_akxsdq.csv"
    setting["LOG_FILE"] = "../spider_log/05_akxsdq_{}_{}_{}.log".format(today.year, today.month, today.day)
    setting["CONCURRENT_REQUESTS"] = 5
    # setting["ITEM_PIPELINES"] = {}
    process = CrawlerProcess(setting)
    process.crawl("05_akxsdq")
    process.start()
