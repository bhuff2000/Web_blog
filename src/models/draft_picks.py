__author__ = 'behou'

import uuid
from src.models.rooms import Room
from random import seed,choice



class Draft_Picks(object):
    def __init__(self, room_id, username, pool_pick_num, user_pick_num, car_num, drv_full, _id=None):
        self.room_id = room_id,
        self.username = username,
        self.pool_pick_num = pool_pick_num
        self.user_pick_num = user_pick_num,
        self.car_num = car_num,
        self.drv_full = drv_full,
        self._id = uuid.uuid4().hex if _id is None else _id

    def json(self):
        return {
            'room_id': self.room_id,
            'username': self.username,
            'pool_pick_num': self.pool_pick_num,
            'user_pick_num': self.user_pick_num,
            'car_num': self.car_num,
            'drv_full': self.drv_full,
            '_id': self._id
        }


    @classmethod
    def draft_order(cls, room_id):
        members = Room.get_room_members(room_id)
        member_list = []
        for member in members:
            member_list.append(member.username)
        return member_list

    @classmethod
    def pick_order(cls, member_list):
        members = member_list
        num = members.count()
        print(num)
        pick_list =[]
        seed(1)
        sequence = [i for i in range(100)]
        print (sequence)
        x=0
        for _ in range(num):
            selection = choice(sequence)
            pick_list.append((members[x], selection))
            print(pick_list)
            x = x+1
        print(pick_list)

    def create_and_save_pick_list(self):
        pass




