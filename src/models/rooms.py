from flask_login import current_user

from src.models.members import Room_Member

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
        room_data = Room.get_room_by_name(self.room_name)
        member_to_add = Room_Member(room_data._id, room_data.room_name, room_data.created_by, room_data.created_by, is_room_admin=True)
        member_to_add.add_room_member()



    @classmethod
    def get_room_by_id(cls, _id):
        room = Database.find_one('rooms', {'_id': _id})
        return cls (**room)

    @classmethod
    def get_room_by_name(cls, room_name):
        room = Database.find_one('rooms', {'room_name': room_name})
        return cls(**room)

    @classmethod
    def find_by_roomname_and_username(cls, room_name, username):
        data = Database.find_one("rooms", {"$and": [{"room_name": room_name}, {"username": username}]})
        return data

    @classmethod
    def get_room_members(cls, room_id):
        members= Database.find('members', {'room_id': room_id})
        return cls(**members)

