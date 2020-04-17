__author__ = 'behou'

from datetime import datetime
from src.common.database import Database

class Message(object):
    def __init__(self, room_name, text, sender, created_at=datetime.now()):
        self.room_name = room_name
        self.text = text
        self.sender = sender
        self.created_at = created_at

    def json(self):
        return {
            'room_name': self.room_name,
            'text': self.text,
            'sender': self.sender,
            'created_at': self.created_at
        }

    def save_message(self):
        Database.insert(collection='messages',
                        data=self.json())

    @classmethod
    def get_messages(cls, room_name):
        messages = Database.find_one('rooms', {'room_name': room_name})
        if messages is not None:
            return cls(**messages)
        else:
            messages = {'sender': 'na', 'created_at': 'na', 'text': 'No messages yet'}
            return messages
