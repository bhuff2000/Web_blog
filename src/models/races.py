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

    @classmethod
    def extract_sportradar_data(cls, data):
        sr_data = []
        json_file = json.loads(data)
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
    def find_by_year(cls, year):
        races = Database.find(collection='races',
                              query={'year': year})
        return [cls(**race) for race in races]