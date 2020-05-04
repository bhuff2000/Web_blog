__author__ = 'behou'

import uuid
from src.models.rooms import Room
from random import seed,choice, randint
from src.common.database import Database



class Draft_Picks(object):
    def __init__(self, room_id, username, pool_pick_num, user_pick_num, car_num=None, drv_full=None, _id=None):
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

    def save_to_mongo(self):
        Database.insert("picks", self.json())

    @classmethod
    def draft_order(cls, room_id):
        print(room_id)
        members = Room.get_room_members(room_id)
        print(members[0])
        member_list = []
        for member in members:
            member_list.append(member['username'])
        return member_list, room_id

    @classmethod
    def pick_order(cls, member_list, room_id):
        members = member_list
        collection = Database.DATABASE['members']
        num = collection.find().count_documents({})
        print(type(collection))
        pick_list =[]
        #seed(1)
        #sequence = [i for i in range(100)]
        #print (sequence)
        x=0
        for _ in range(num):
            #selection = choice(sequence)
            number = randint(0,1000)
            pick_list.append((member_list[x]['username'], number))
            print(pick_list)
            x = x+1
        return sorted(pick_list, key = lambda x: x[1])

    @classmethod
    def create_and_save_pick_list(cls, room_id):

        #  from room_id run draft_order method to obtain list of members
        # use list of members to then run pick_order method
        # pick_order method will provide the number of members and the order in which they will pick drivers
        #
        room_members = Draft_Picks.draft_order(room_id)
        ordered_members = Draft_Picks.pick_order(room_members, room_id)

        num_members = len(room_members)
        num_picks = 5
        total_picks = num_members*num_picks

        # run loop for total number of picks and create a Draft-Pick object each time through the loop
        # and save object to database

        group = 1
        for i in range(total_picks):
            if not (group%2) == 0:
                for member in ordered_members:
                    pick = Draft_Picks(room_id, member, i, group)
                    pick.save_to_mongo()
            else:
                for member in reversed(ordered_members):
                    pick = Draft_Picks(room_id, member, i, group)
                    pick.save_to_mongo()
            group = group + 1

        return ordered_members


