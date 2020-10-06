import os

import pymongo
import urllib.parse

class Database(object):
    URI = os.environ.get("DB_URI")
    #USERNAME = os.environ.get("DB_USERNAME")
    #PASSWORD = os.environ.get("DB_PASSWORD")
    #username = 'behoughton@yahoo.com'
    #password = '$araAbby38'
    #URI = urllib.parse.quote_plus(UNPARSED_URI)
    #print(URI)
    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client['heroku_m56h929h']

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def update_one(collection, query, new_vals):
        return Database.DATABASE[collection].update_one(query, new_vals)

    @staticmethod
    def replace_one(collection, query, new_vals):
        return Database.DATABASE[collection].replace_one(query, new_vals)