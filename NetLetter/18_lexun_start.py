from datetime import datetime

import redis
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def conn_redis():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    return r


def start_script(csvfilename, logfile, crawl, redis_delset=None):
    conn_redis_ = conn_redis()
    # set
    if redis_delset:
        conn_redis_.delete(redis_delset)
    setting_ = get_project_settings()
    # add settings
    setting_["csv_filename"] = csvfilename
    setting_["LOG_FILE"] = "../spider_log/%s" % logfile
    process = CrawlerProcess(settings=setting_)
    process.crawl(crawl)
    process.start()


if __name__ == '__main__':
    # 存储csv
    csvfilename = "18_lexun.csv"
    today = datetime.now()
    # 运行的spider
    crawl = "18_lexun"
    # redis去重链接集合,str
    redis_delset = None
    # 日志文件
    logfile = "18_lexun_{}_{}_{}.log".format(today.year, today.month, today.day)
    start_script(csvfilename, logfile, crawl, redis_delset)
