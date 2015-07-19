# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from pymongo import MongoClient
from os import environ
from scrapy.exceptions import DropItem

MONGODB_URI = 'mongodb://%s:%s@%s:%d/%s' % (
environ['MONGO_DBUSER'], environ['MONGO_DBPASSWORD'], environ['MONGO_URL'], int(environ['MONGO_PORT']),
environ['MONGO_DBNAME'])

class PeliscraperPipeline(object):
    def process_item(self, item, spider):
        return item

class MongoPipeline(object):

    collection_name = 'movies'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=MONGODB_URI,
            mongo_db=environ['MONGO_DBNAME']
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # Does the item already exist?
        query = {'movie_id': item['movie_id']}
        doc = self.db[self.collection_name].find_one(query)
        if doc:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.db[self.collection_name].insert(dict(item))
            return item
