# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import csv
import logging
import os
import time

from .mongo_ import MongoL

logger = logging.getLogger(__name__)


class NetletterPipeline:
    def process_item(self, item, spider):
        return item


class CsvPipeline:
    def __init__(self, csv_filename="default.csv"):
        store_dir = os.path.dirname(__file__) + "/csv_data/"
        if "\\" in store_dir:
            store_dir = store_dir.replace("\\", "/")
        if not os.path.exists(store_dir):
            os.mkdir(store_dir)
        store_file = store_dir + csv_filename
        self.file = open(store_file, 'w', newline='', encoding='utf-8')
        self.fieldnames = ['url', 'username']
        self.writer = csv.DictWriter(f=self.file, fieldnames=self.fieldnames)
        self.writer.writeheader()

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        csv_filename = settings.get("csv_filename")
        return cls(csv_filename)

    def process_item(self, item, spider):
        self.writer.writerow({"url": item["url"], "username": item["username"]})
        return item

    def close_spider(self, spider):
        self.file.close()


class MongoPipeline:

    def __init__(self):
        mongo = MongoL()
        self.mongo_cli, self.collection = mongo.mongo_col()

    def process_item(self, item, spider):
        if "www.zhuafan.live" in item["url"]:
            data = {"app_id": 39, "module_id": 41, "result": item["username"],
                    "result_url": item["url"], "app_type_key": "live", "origin": {}, "ct": int(time.time())}
            res = self.collection.update_one({"app_id": 39, "module_id": 41, "result": data.get("result")},
                                             {"$set": data},
                                             upsert=True)
            logger.info("updata_count:%s,instering:%s" % (res.matched_count, data))
        elif "yabolive.com" in item["url"]:
            data = {"app_id": 40, "module_id": 42, "result": item["username"],
                    "result_url": item["url"], "app_type_key": "live", "origin": {}, "ct": int(time.time())}
            res = self.collection.update_one({"app_id": 40, "module_id": 42, "result": data.get("result")},
                                             {"$set": data},
                                             upsert=True)
            logger.info("updata_count:%s,instering:%s" % (res.matched_count, data))

        return item

    def close_spider(self, spider):
        self.mongo_cli.close()


class PostMongoPipeline:
    def open_spider(self, spider):
        mongo = MongoL()
        self.mongo_cli, self.collection = mongo.mongo_col('spider_item_post')
        self.collection.create_index('url', unique=True)

    def process_item(self, item, spider):
        self.collection.replace_one({'url': item['url']}, dict(item), upsert=True)
        return item

    def close_spider(self, spider):
        self.mongo_cli.close()
