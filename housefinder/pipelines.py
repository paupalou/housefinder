import json
import codecs
import pymongo
import re


class JsonPipeline(object):
    def __init__(self):
        self.file = codecs.open('idealista.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()


class MongoPipeline(object):

    collection_name = 'houses'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'housefinder')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        try:
            item['meters'] = int(item['meters'])
            item['rooms'] = int(item['rooms'])
            if type(item['price']) is str:
                item['price'] = int(item['price'].replace('.', ''))
            else:
                item['price'] = item['price']
        except Exception:
            number = re.compile(r'(\d+)')
            item['meters'] = int(number.findall(item['meters']).pop())
            item['rooms'] = int(number.findall(item['rooms']).pop())
            if type(item['price']) is str:
                item['price'] = int(item['price'].replace('.', ''))
            else:
                item['price'] = item['price']
        finally:
            self.db[self.collection_name].insert(dict(item))

        return item
