# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NetletterItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


# 用户昵称
class GeneralItem(scrapy.Item):
    url = scrapy.Field()
    username = scrapy.Field()


# 帖子
class PostItem(scrapy.Item):
    url = scrapy.Field()
    spider_name = scrapy.Field()
    author = scrapy.Field()
    datetime = scrapy.Field()
    title = scrapy.Field()
    context = scrapy.Field()
    ct = scrapy.Field()
