from src.common.database import Database

__author__ = 'behou'



class Test(object):
    def __init__(self, user, message):
        self.user = user
        self.message = message

    def json(self):
        return {
            'user': self.user,
            'message': self.message

        }

    def save_to_mongo(self):
        Database.insert('test', self.json())