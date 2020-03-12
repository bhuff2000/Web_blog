import json

from src.common.database import Database

__author__ = 'behou'

class Sched_Event(object):
    def __init__(self, series, year, event_id, event_name, event_date, track, race_name, race_id, race_status, race_start):
        self.series = series
        self.year = year
        self.event_id = event_id
        self.event_name = event_name
        self.event_date = event_date
        self.track = track
        self.race_name = race_name
        self.race_id = race_id
        self.race_status = race_status
        self.race_start = race_start

    def json(self):
        return {
            'series': self.series,
            'year': self.year,
            'event_id': self.event_id,
            'event_name': self.event_name,
            'event_date': self.event_date,
            'track': self.track,
            'race_name': self.race_name,
            'race_id': self.race_id,
            'race_status': self.race_status,
            'race_start': self.race_start
         }

    def save_to_mongo(self):
        Database.insert("races", self.json())

    def get_race_id(self):
        return self.race_id

    @classmethod
    def extract_sportradar_data(cls, data):
        sr_data = []
        json_file = data
        json_file2 = json_file['events']
        series = json_file['series']['alias']
        year = json_file['season']['year']
        for event in json_file2:
            event_id = event['id']
            event_name = event['name']
            event_date = event['start_date']
            track = event['track']['name']
            races = event['races']
            for race in races:
                race_name = race['name']
                race_id = race['id']
                race_status = race['status']
                race_start = race['scheduled']
                race_ev = Sched_Event(series, year, event_id, event_name, event_date, track, race_name, race_id,
                                   race_status, race_start)
                sr_data.append(race_ev)
        return sr_data

    @classmethod
    def find_by_race_id(cls, race_id):
        data = Database.find_one("races", {"race_id": race_id})
        if data is None:
            return True
        else:
            return False



 #   @classmethod
 #   def define_load_list(cls, sr_data):
 #       loaded = []
 #       to_be_loaded = []
 #       load_list = sr_data
 #       for item in load_list:
 #           pop_item = item.pop()
 #           race_id = pop_item.get_race_id()
 #           if Sched_Event.find_by_race_id(race_id) is True:
 #               to_be_loaded.append(pop_item)
 #           else:
 #               loaded.append(pop_item)
 #       return to_be_loaded, loaded


    @classmethod
    def find_by_year(cls, year):
        races = Database.find(collection='races',
                              query={'year': int(year)})
        races_list = []
        for race in races:
            races_list.append(race)
        return races_list

    @classmethod
    def find_by_series(cls, series):
        races = Database.find(collection='races',
                              query={'series': series})
        races_list = []
        for race in races:
            races_list.append(race)
        one_race = {"race_name":"Daytona 500"}
        return one_race