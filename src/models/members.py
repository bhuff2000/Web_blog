__author__ = 'behou'

from src.common.database import Database
import datetime



class Room_Member(object):
    def __init__(self, room_id, room_name, username, added_by, is_room_admin):
        self.room_id = room_id
        self.room_name = room_name
        self.username = username
        self.added_by = added_by
        self.is_room_admin = is_room_admin
        self._id = {'room_id': self.room_id, 'username': self.username}


    def json(self):
        return {
            'room_id': self.room_id,
            'room_name': self.room_name,
            'username': self.username,
            'added_by': self.added_by,
            'is_room_admin': self.is_room_admin,
            '_id': self._id
        }

    def add_room_member(self):
        member = Database.insert('members', data=self.json())
