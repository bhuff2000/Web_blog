__author__ = 'behou'

import json

from src.common.database import Database

__author__ = 'behou'

class Entrants(object):
    def __init__(self, race_id, race_name, car_num, crew_chief, mfg, owner_id, team_id, drv_first,
                 drv_last, drv_full, drv_id):
        self.race_id = race_id
        self.race_name = race_name
        self.car_num = car_num
        self.crew_chief = crew_chief
        self.mfg = mfg
        self.owner_id = owner_id
        self.team_id = team_id
        self.drv_first = drv_first
        self.drv_last = drv_last
        self.drv_full = drv_full
        self.drv_id = drv_id

    def json(self):
        return {
            'race_id': self.race_id,
            'race_name': self.race_name,
            'car_num': self.car_num,
            'crew_chief': self.crew_chief,
            'mfg': self.mfg,
            'owner_id': self.owner_id,
            'team_id': self.team_id,
            'drv_first': self.drv_first,
            'drv_last': self.drv_last,
            'drv_full': self.drv_full,
            'drv_id': self.drv_id
         }

    def save_to_mongo(self):
        Database.insert("entrants", self.json())

    def get_race_id(self):
        return self.race_id

    def get_drv_id(self):
        return self.drv_id

    @classmethod
    def extract_sportradar_data(cls, data):
        sr_data = []
        json_file = data
        json_file2 = json_file['entry_list']
        if json_file['id'] is  not None:
            race_id = json_file['id']
        else:
            race_id = "na"
        race_name = json_file['name']
        #year = json_file['season']['year']
        for entrant in json_file2:
            car_num = entrant['car']['number']
            #ownerID = entrant['car']['owner']
            if 'crew_chief' in entrant['car'] :
                crew_chief = entrant['car']['crew_chief']
            else:
                crew_chief = "na"
            mfg = entrant['car']['manufacturer']['name']
            if 'owner' in entrant['car']:
                owner_id = entrant['car']['owner']['id']
            else:
                owner_id = 'na'
            if 'team' in entrant['car']:
                team_id = entrant['car']['team']['id']
            else:
                team_id = 'na'
            drv_first = entrant['driver']['first_name']
            drv_last = entrant['driver']['last_name']
            drv_full = entrant['driver']['full_name']
            drv_id = entrant['driver']['id']
            driver = Entrants(race_id, race_name, car_num, crew_chief, mfg, owner_id, team_id, drv_first, drv_last,
                                      drv_full, drv_id)
            sr_data.append(driver)
        return sr_data

    @classmethod
    def find_by_race_and_drv_id(cls, race_id, driver_id):
        data = Database.find_one("entrants", {"$and": [{"race_id": race_id}, {"drv_id": driver_id}]})

        if data is None:
            return True
        else:
            return False

    @classmethod
    def find_drivers_by_race_id(cls, race_id):
        data = Database.find("entrants", {"race_id": race_id})
        driver_list = []
        for driver in data:
            driver_list.append(driver)
            driver_list.sort()
        return driver_list
