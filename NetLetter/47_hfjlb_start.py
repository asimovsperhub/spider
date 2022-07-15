from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


if __name__ == '__main__':
    setting_ = get_project_settings()
    today = datetime.now()
    setting_["csv_filename"] = "47_hfjlb.csv"
    setting_["CONCURRENT_REQUESTS"] = 2
    setting_["LOG_FILE"] = "../spider_log/47_hfjlb_{}_{}_{}.log".format(today.year, today.month, today.day)
    process = CrawlerProcess(settings=setting_)
    process.crawl("hfjlb")
    process.start()
