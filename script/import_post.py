# 导入 spider_item_post 到 spider_result
# python -m script.import_post

import pymongo
from pymongo.operations import InsertOne, ReplaceOne
from scrapy.utils.project import get_project_settings

settings = get_project_settings()
mongo_host = settings['MONGODB']

mongo_cli = pymongo.MongoClient(host=mongo_host)

db = mongo_cli.get_database('spiders')

result_col = db.get_collection('spider_result')
post_col = db.get_collection('spider_item_post')


APP_MODULE_MAP = {
    "02_oppo":        {"app_id": 8,  "module_id": 31, 'app_type_key': "news"},
    "17_post_kuan":   {"app_id": 27, "module_id": 32, 'app_type_key': "social"},
    "45_hgh":         {"app_id": 35, "module_id": 34, 'app_type_key': "news"},
    "09_post_glh":    {"app_id": 20, "module_id": 33, 'app_type_key': "community"},
    "18_post_lenxun": {"app_id": 31, "module_id": 35, 'app_type_key': "community"},
    "30_post_szwb":   {"app_id": 4,  "module_id": 36, 'app_type_key': "social"},
    "33_post_fw":     {"app_id": 17, "module_id": 37, 'app_type_key': "community"},
}

for spider_name, apps in APP_MODULE_MAP.items():
    data = [
        InsertOne(dict(
            **apps,
            result=v['context'],
            result_url=v['url']
        )) for v in post_col.find({"spider_name": spider_name})
    ]
    print(f'do "{spider_name}" len(data)={len(data)}')
    res = result_col.bulk_write(data)
    print(res)
