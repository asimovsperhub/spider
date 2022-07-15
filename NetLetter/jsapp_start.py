from datetime import datetime

import redis
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def conn_redis():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    return r


if __name__ == '__main__':
    # conn_redis_ = conn_redis()
    # # set
    # conn_redis_.delete("dgtle_url")
    setting_ = get_project_settings()
    # add settings
    today = datetime.now()
    setting_["csv_filename"] = "jsapp.csv"
    setting_["LOG_FILE"] = "../spider_log/jsapp_{}_{}_{}.log".format(today.year, today.month, today.day)
    process = CrawlerProcess(settings=setting_)
    process.crawl("jsapp")
    process.start()

