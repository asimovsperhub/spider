from datetime import datetime

import redis
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def conn_redis():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    return r


def start_script(csvfilename, logfile, crawl, redis_delset=None):
    # set
    if redis_delset:
        conn_redis_ = conn_redis()
        conn_redis_.delete(redis_delset)
    setting_ = get_project_settings()
    # add settings
    setting_["csv_filename"] = csvfilename
    # delay 3s
    setting_["DOWNLOAD_DELAY"] = 3
    setting_["CONCURRENT_REQUESTS"] = 2
    setting_["DOWNLOADER_MIDDLEWARES"] = {
        'NetLetter.middlewares.TooManyRequestsRetryMiddleware': 543,
        'NetLetter.middlewares.ProxyMiddleware': 544
    }
    setting_["LOG_FILE"] = "../spider_log/%s" % logfile
    process = CrawlerProcess(settings=setting_)
    process.crawl(crawl)
    process.start()


if __name__ == '__main__':
    # 存储csv
    csvfilename = "41_zaw.csv"
    today = datetime.now()
    # 运行的spider
    crawl = "41_zaw"
    # redis去重链接集合,str
    redis_delset = None
    # 日志文件
    logfile = "41_zaw_{}_{}_{}.log".format(today.year, today.month, today.day)
    start_script(csvfilename, logfile, crawl, redis_delset)
