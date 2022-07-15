# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import linecache
import logging
import random
import time

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class NetletterSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class NetletterDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ProxyMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    # 设置代理
    # def process_request(self, request, spider):
    #     # Called for each request that goes through the downloader
    #     # middleware.
    #
    #     # Must either:
    #     # - return None: continue processing this request
    #     # - or return a Response object
    #     # - or return a Request object
    #     # - or raise IgnoreRequest: process_exception() methods of
    #     #   installed downloader middleware will be called
    #     proxy = str(self.get_id(), encoding="utf-8")
    #     spider.logger.info("proxy：%s" % proxy)
    #     request.meta["proxy"] = proxy

    def process_response(self, request, response, spider):
        # spider.logger.info(response.status)
        # 终止爬虫，设置代理并重新返回给调度器
        if response.status == 302:
            ip = self.get_id()
            request.meta["proxy"] = ip
            # print("返回不等于200，更新代理ip:%s" % ip)
            # print("代理", request.meta.get("proxy"))
            spider.logger.info("response:%s,set ip : %s" % (response.status, ip))
            return request
        return response

    # 请求异常时，更换代理
    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        ip = self.get_id()
        request.meta["proxy"] = ip
        # print("异常，更新代理ip:%s" % request.meta.get("proxy"))
        spider.logger.info("exception updata proxy:%s" % request.meta.get("proxy"))
        return request

    def get_id(self):
        line = random.randint(1, 130)
        ip = linecache.getline("./ippool.txt", line).split("\n")[0]
        return ip

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# 重写scrapy重试中间件
class TooManyRequestsRetryMiddleware(RetryMiddleware):

    def __init__(self, crawler):
        super(TooManyRequestsRetryMiddleware, self).__init__(crawler.settings)
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        elif response.status == 429:
            # 暂停执行引擎
            spider.logger.info("429 start pause spiders")
            self.crawler.engine.pause()
            pause_time = random.randint(3, 5)
            time.sleep(pause_time)
            spider.logger.info("429 start pause spiders time :%s" % pause_time)
            # 恢复执行引擎
            self.crawler.engine.unpause()
            spider.logger.info("429 start unpause spiders")
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        elif response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        return response


class SeleniumMiddleware:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=chrome_options)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    #
    def process_request(self, request, spider):
        try:
            self.driver.get(request.url)
            # if self.driver.find_element_by_class_name("warncontenter"):
            #     pass
            # city_class = driver.find_element_by_class_name("city-layer")
            count = self.driver.find_element_by_xpath('/html/body/div[3]/div[3]/div[1]/span').text
            count = int(count)
            pages = count / 20
            if count < 20:
                page_ = 1
            else:
                page_ = int(pages) + 1

            for i in range(1, page_ + 1):
                self.driver.get(request.url)
                user_list = self.driver.find_elements_by_xpath('//*[@id="find_broker_lists"]/ul/li')
                for i in user_list:
                    for d in i.find_elements_by_xpath('./div[1]/div[1]/p/b/a'):
                        print(d.text)
        except Exception as e:
            spider.logger.error(e)

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
