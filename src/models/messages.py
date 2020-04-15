__author__ = 'behou'

from datetime import datetime
from src.common.database import Database

class Message(object):
    def __init__(self, room_id, text, sender, created_at=datetime.now()):
        self.room_id = room_id
        self.text = text
        self.sender = sender
        self.created_at = created_at

    def json(self):
        return {
            'room_id': self.room_id,
            'text': self.text,
            'sender': self.sender,
            'created_at': self.created_at
        }

    def save_message(self):
        Database.insert(collection='messages',
                        data=self.json())

    @classmethod
    def get_messages(cls, room_id):
        messages = Database.find_one('rooms', {'room_id': room_id})
        if messages is not None:
            return cls(**messages)
        else:
            messages = {'sender': 'na', 'created_at': 'na', 'text': 'No messages yet'}
            return messages
