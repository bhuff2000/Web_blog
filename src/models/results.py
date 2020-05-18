__author__ = 'behou'

import json

from src.common.database import Database

__author__ = 'behou'

class Results(object):
    def __init__(self, race_id, race_name, race_status, track_id, start_pos, position, drv_status, points, bonus_points,
                   penalty_points, stage_1_points, stage_2_points, laps_led, laps_completed, car_num, car_id,
                   crew_chief, mfg, owner_id, team_id, drv_first, drv_last, drv_full, drv_id):
        self.race_id = race_id
        self.race_name = race_name
        self.race_status = race_status
        self.track_id = track_id
        self.start_pos= start_pos
        self.position = position
        self.drv_status = drv_status
        self.points = points
        self.bonus_points = bonus_points
        self.penalty_points = penalty_points
        self.stage_1_points = stage_1_points
        self.stage_2_points = stage_2_points
        self.laps_led = laps_led
        self.laps_completed = laps_completed
        self.car_num = car_num
        self.car_id = car_id
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
            'race_status': self.race_status,
            'track_id': self.track_id,
            'start_pos': self.start_pos,
            'position': self.position,
            'drv_status': self.drv_status,
            'points': self.points,
            'bonus_points': self.bonus_points,
            'penalty_points': self.penalty_points,
            'stage_1_points': self.stage_1_points,
            'stage_2_points': self.stage_2_points,
            'laps_led': self.laps_led,
            'laps_completed': self.laps_completed,
            'car_num': self.car_num,
            'car_id': self.car_id,
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
        Database.insert("results", self.json())

    @classmethod
    def extract_sportradar_data(cls, data):
        sr_data = []
        json_file = data
        json_file2 = json_file['results']
        print(str(json_file2))
        if json_file['id'] is not None:
            race_id = json_file['id']
        else:
            race_id = "na"

        race_name = json_file['name']
        track_id = json_file['track']['id']
        race_status = json_file['status']
        # year = json_file['season']['year']
        for result in json_file2:
            car_num = result['car']['number']
            # ownerID = entrant['car']['owner']
            if 'crew_chief' in result['car']:
                crew_chief = result['car']['crew_chief']
            else:
                crew_chief = "na"
            mfg = result['car']['manufacturer']['name']
            if 'owner' in result['car']:
                owner_id = result['car']['owner']['id']
            else:
                owner_id = 'na'
            if 'team' in result['car']:
                team_id = result['car']['team']['id']
            else:
                team_id = 'na'


            start_pos = result['start_position']
            position = result['position']
            drv_status = result['status']
            points = result['points']
            bonus_points = result['bonus_points']
            penalty_points = result['penalty_points']
            stage_1_points = result['stage_1_points']
            stage_2_points = result['stage_2_points']
            laps_led = result['laps_led']

            if 'laps_completed' in result:
                laps_completed = result['laps_completed']
            else:
                laps_completed = "na"
            car_id = result['car']['id']
            drv_first = result['driver']['first_name']
            drv_last = result['driver']['last_name']
            drv_full = result['driver']['full_name']
            drv_id = result['driver']['id']
            results = Results(race_id, race_name, race_status, track_id, start_pos, position, drv_status, points, bonus_points,
                   penalty_points, stage_1_points, stage_2_points, laps_led, laps_completed, car_num, car_id,
                   crew_chief, mfg, owner_id, team_id, drv_first, drv_last, drv_full, drv_id)
            sr_data.append(results)
        return sr_data

    def get_race_id(self):
        return self.race_id

    def get_drv_id(self):
        return self.drv_id

    @classmethod
    def find_by_race_and_drv_id(cls, race_id, driver_id):
        data = Database.find_one("results", {"$and": [{"race_id": race_id}, {"drv_id": driver_id}]})

        if data is None:
            return True
        else:
            return False

    @classmethod
    def results_by_race_id(cls, race_id):
        data = Database.find("results", {"race_id": race_id})
        result_list = []
        for result in data:
            result_list.append(result)
        return sorted(result_list, key=lambda i: (i['position']))

    @classmethod
    def get_position_by_race_id_driver_name(cls, race_id, drv_full):
        position = Database.find_one("results", {"$and": [{"race_id": race_id}, {"drv_full: drv_full"}]})
        return position