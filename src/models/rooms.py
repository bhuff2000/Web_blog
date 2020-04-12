from flask_login import current_user

__author__ = 'behou'
from src.common.database import Database
import datetime
import uuid

class Room(object):
    def __init__(self, room_name, created_by, created_at=datetime.datetime.now(), _id=None):
        self.room_name = room_name
        self.created_by = created_by
        self.created_at = created_at
        self._id = uuid.uuid4().hex if _id is None else _id

    def json(self):
        return {
            'room_name': self.room_name,
            'created_by': self.created_by,
            'created_at': self.created_at,
            '_id': self._id
        }

    def save_room(self):
        Database.insert(collection='rooms',
                        data=self.json())
    @classmethod
    def get_room_by_id(cls, _id):
        room = Database.find_one('rooms', {'room_id': _id})
        return room

    @classmethod
    def get_room_by_name(cls, room_name):
        room = Database.find_one('rooms', {'room_name': room_name})
        return room

