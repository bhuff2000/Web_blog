__author__ = 'behou'

import uuid
from src.models.rooms import Room
from random import seed,choice, randint
from src.common.database import Database



class Draft_Picks(object):
    def __init__(self, room_id, username, pool_pick_num, user_pick_num, car_num=None, drv_full=None, _id=None):
        self.room_id = room_id,
        self.username = username,
        self.pool_pick_num = pool_pick_num,
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
    def update_pick(cls, room_id, username, pick_num, car_num, drv_full):
        query = {"$and": [{"room_id": room_id}, {"username": username}, {"pool_pick_num": pick_num}]}
        data = Database.DATABASE.find_one("picks", query)
        print(str(data["drv_full"]))
        print(str(query))
        values = {"car_num": car_num, "drv_full": drv_full}
        print(str(values))
        new_vals = {"$set": values}
        print(str(new_vals))
        Database.DATABASE.update_one('picks', query, new_vals)


    @classmethod
    def draft_order(cls, room_id):
        print(room_id)
        members = Room.get_room_members(room_id)

        member_list = list(members)
        print(type(member_list))
        #for member in members:
        #    member_list.append(member['username'])
        return member_list

    @classmethod
    def pick_order(cls, member_list, room_id):
        #members = member_list.username
        #print('stuff ' + str(member_list))
        collection = Database.DATABASE['members']
        num = collection.count({"room_id": room_id})
        print(str(num))
        pick_list =[]
        #seed(1)
        #sequence = [i for i in range(100)]
        #print (sequence)
        z= int(0)
        for member in member_list:
            #selection = choice(sequence)
            number = randint(0,1000)
            #pick_list.append((member['username'], number))
            pick_list.append({"username": member["username"], "number": number})
            print(pick_list)
            z = z+1
        return sorted(pick_list, key = lambda x: x["number"])

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
        print('total picks ' + str(total_picks))

        # run loop for total number of picks and create a Draft-Pick object each time through the loop
        # and save object to database
        pool_pick=1
        group = 1
        i=1
        for i in range(num_picks):
            if not (group%2) == 0:
                for member in ordered_members:
                    pick = Draft_Picks(room_id, member, pool_pick, i+1)
                    print('pick ' + str(pick.json()) + ' group ' + str(pool_pick) + ' odd  ' + str(i))
                    pick.save_to_mongo()
                    pool_pick = pool_pick+1
            else:
                for member in reversed(ordered_members):
                    pick = Draft_Picks(room_id, member, pool_pick, i+1)
                    print('pick ' + str(pick.json()) + ' group ' + str(pool_pick) + ' even ' + str(i))
                    pick.save_to_mongo()
                    pool_pick = pool_pick + 1
            group = group + 1

        return ordered_members


