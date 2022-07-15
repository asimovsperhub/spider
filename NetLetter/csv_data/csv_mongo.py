import logging
import os
import time
from datetime import datetime
from pymongo import UpdateOne
import pandas as pd

# from ..mongo_ import MongoL

import pymongo
import redis
from scrapy.utils.project import get_project_settings
from loguru import logger
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.exceptions import NotFoundError
from elasticsearch.helpers import bulk

settings = get_project_settings()

config = {
    "handlers": [
        {
            "sink": "/home/root1/NetLetter/spider_log/csv_mongo.log",
            # log size, > 50MB : auto create new log
            "rotation": "500 MB",
            # clean  days/minutes/seconds/ ago   log
            # "retention":"10 days",
            #
            "serialize": False,
            # format
            # "format": "<level>{time}</level>|<level>{level}</level>|<cyan>{name}</cyan>:<cyan>{function}</cyan>-filename:<cyan>{file}</cyan>:<cyan>{line}</cyan>-process:<cyan>{process.name}</cyan>-MESSAGE:<level>{message}</level>",
        }
    ]
}

logger.configure(**config)

es = Elasticsearch(
    'es-cn-7mz25ejbo0002adly.elasticsearch.aliyuncs.com',
    http_auth=('elastic', '9j1cwYZLamvc'),
    port=9200,
    use_ssl=False
)


class MongoL(object):

    def mongo_col(self):
        settings = get_project_settings()
        mongo_host = settings['MONGODB']
        mongo_cli = pymongo.MongoClient(
            host=mongo_host,
            readPreference='secondaryPreferred'
        )

        mongo_db = pymongo.database.Database(mongo_cli, 'spiders')
        collection = pymongo.collection.Collection(mongo_db, "spider_result")
        return mongo_cli, collection


class CsvMongo(object):

    def __init__(self):
        self.__file_list = []
        mongo = MongoL()
        self.__mongo_cli, self.__collection = mongo.mongo_col()

    def csv_file(self, dir_path):

        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if ".csv" in file:
                    self.__file_list.append(file)

        return self.__file_list

    def write_db(self, file, app_id, module_id, app_type_key):
        read_ = pd.read_csv(file, chunksize=10000, usecols=['url', 'username'])
        for dg in read_:
            for _, line in dg.iterrows():
                ops = []
                _source = []
                es_ = []
                url = line[0]
                username = line[1]
                data = {"app_id": app_id, "module_id": module_id, "result": username,
                        "result_url": url, "app_type_key": app_type_key, "origin": {},
                        "ct": int(time.time())}
                ops.append(UpdateOne({"app_id": app_id, "module_id": module_id, "result_url": data.get("result_url")},
                                     {"$set": data},
                                     upsert=True))
                es_result = data.copy()
                es_result.update({"scan_result": data.get("result_url")})
                es_result.pop("result_url")
                _source.append(es_result)
                if ops:
                    res = self.__collection.bulk_write(ops)
                    logger.info("updata_count:%s,instering:%s" % (res.matched_count, ops))
                    ids = res.upserted_ids
                    # 全是插入的话
                    if len(ids) == len(es_result):
                        for i, va in enumerate(es_result):
                            a1 = {"_index": "risk_detection", "_source": va, "_id": ids.get(i)}
                            es_.append(a1)
                        res, _ = bulk(es, es_, index="risk_detection", raise_on_error=True)

    # def find_

    def csv_mongo(self, file, app_module_id, app_type_key="community"):
        self.write_db(file=file, app_id=app_module_id, module_id=app_module_id, app_type_key=app_type_key)


if __name__ == '__main__':
    cm = CsvMongo()
    files = cm.csv_file(os.path.dirname(os.path.abspath(__file__)))
    for file in files:
        if file == "loovee.csv":
            cm.csv_mongo(file, 26, "social")
