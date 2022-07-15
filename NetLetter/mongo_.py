from typing import Tuple
import pymongo
from pymongo.database import Database
from pymongo.collection import Collection
import redis
from scrapy.utils.project import get_project_settings

settings = get_project_settings()

user_agents = settings['USER_AGENTS']


class MongoL(object):

    def mongo_col(self, table_name='spider_result') -> Tuple[pymongo.MongoClient, Collection]:
        settings = get_project_settings()
        mongo_host = settings['MONGODB']
        mongo_cli = pymongo.MongoClient(
            host=mongo_host,
            readPreference='secondaryPreferred'
        )

        mongo_db = pymongo.database.Database(mongo_cli, 'spiders')
        collection = pymongo.collection.Collection(mongo_db, table_name)
        return mongo_cli, collection


class RedisL(object):

    def conn_redis(self):
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        return r


if __name__ == '__main__':
    red = RedisL()
    conn = red.conn_redis()
    for i in conn.sscan("dgtle_url"):
        print(i)
