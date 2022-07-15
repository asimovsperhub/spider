from datetime import datetime

import redis
from fake_useragent import UserAgent
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
    setting_["LOG_FILE"] = "../spider_log/%s" % logfile
    setting_["DEFAULT_REQUEST_HEADERS"] = {
        'User-Agent': str(UserAgent(verify_ssl=False).random),
        # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': "user_locale=zh-CN; oschina_new_user=false; remote_way=http; tz=Asia%2FShanghai; Hm_lvt_24f17767262929947cc3631f99bfd274=1620642644,1622108416,1623221720; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%229250752%22%2C%22first_id%22%3A%22178f36df8ec75e-0f7ee693ade5-3f356b-2073600-178f36df8ede06%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_utm_source%22%3A%22google%22%2C%22%24latest_utm_medium%22%3A%22sem%22%2C%22%24latest_utm_campaign%22%3A%22enterprise%22%2C%22%24latest_utm_term%22%3A%22giteezsy%22%7D%2C%22%24device_id%22%3A%22178f36df8ec75e-0f7ee693ade5-3f356b-2073600-178f36df8ede06%22%7D; Hm_lvt_9f934b89d116d933387e452cbf2c3fe6=1623222505; Hm_lpvt_9f934b89d116d933387e452cbf2c3fe6=1623222666; gitee_user=true; Hm_lpvt_24f17767262929947cc3631f99bfd274=1623227288; gitee-session-n=MzRwdkxMbUJpdW9mWk1WM1o2ZWVPeWYvMERWckxkYkQ2SGJVcDR6NVRWdmFHUXJvM2JkV1E2RmswY3pXVVZFVnVGcTdqdC9VOTdoTjZ2cEZOZ0xlVjQvUjdaYnpWT2szQ3pOVVRsS1VBeWlTV0ZCLzExeHhLQjhjbUViRndDUzdZY0VuUmx2YzVncUxBdi9iaVRrZi93aDhpTWgrNUVUUTMxazF5RUVqTmhxdGtPOU0yMVdBUkl5MVpRK3hQUDVicUN6bFdsTWlqNmUzTW0zWTZ0VXRLNHg2WjlEYzlZeDZuelNsK1o4ckRSWkMrQVlNSWRRbis3NVM3eHNybE1DRmdrZTVrY01XbDFud29QNG82VllrZXc2bStPNWM1dEhxMk85WjNxaVEvbjREOEIzbGM4eHBNSHJMNjFxaHZEd1N5Z1ByQWxVRHNBMkhkYlNTWmg1SFFJUkNGWU10blZTeXp0aGM0b3FqNzdNPS0tRGs4Tit3eGlqY1IyRDRUbk1sOVF1QT09--68f90b0809715905684aaa6af8e3a4da7a4fa5f0"
    }
    process = CrawlerProcess(settings=setting_)
    process.crawl(crawl)
    process.start()


if __name__ == '__main__':
    # 存储csv
    csvfilename = "20_gtee.csv"
    today = datetime.now()
    # 运行的spider
    crawl = "20_gtee"
    # redis去重链接集合,str
    redis_delset = None
    # 日志文件
    logfile = "20_gtee_{}_{}_{}.log".format(today.year, today.month, today.day)
    start_script(csvfilename, logfile, crawl, redis_delset)
