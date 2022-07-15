import time

import pymongo
from pymongo import UpdateOne


def mongo_col():
    mongo_host = "mongodb://root:kNsPjm0nh5HQ@dds-uf68ff3b207405e41.mongodb.rds.aliyuncs.com:3717,dds-uf68ff3b207405e42.mongodb.rds.aliyuncs.com:3717/admin?replicaSet=mgset-46340684"
    mongo_cli = pymongo.MongoClient(
        host=mongo_host,
        readPreference='secondaryPreferred'
    )

    mongo_db = pymongo.database.Database(mongo_cli, 'spiders')
    collection = pymongo.collection.Collection(mongo_db, "spider_result")
    return mongo_cli, collection


_, col_ = mongo_col()
ops = []
for i in range(100, 105):
    data = {"app_id": i, "module_id": i, "result": "测试",
            "result_url": "测试url", "app_type_key": "test", "origin": {},
            "ct": int(time.time())}
    res = col_.update_one({"app_id": i, "module_id": i, "result_url": data.get("result_url")},
                          {"$set": data},
                          upsert=True)
    print(res.upserted_id)
    # ops.append(UpdateOne({"app_id": "369", "module_id": "369", "result_url": data.get("result_url")},
    #                      {"$set": data},
    #                      upsert=True))
    # if ops:
    #     res = col.bulk_write(ops)
    #     print(res.bulk_api_result)
    #     print(res.upserted_ids)
    # logger.info("updata_count:%s,instering:%s" % (res.matched_count, ops))

    # d = ["a", "b"]
    # # d = {0: "id1", 1: "id2"}
    # for i, va in enumerate(d):
    #     print(i, va)
