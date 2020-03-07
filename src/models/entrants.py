__author__ = 'behou'

import json

from src.common.database import Database

__author__ = 'behou'

class Entrants(object):
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
        Database.insert("entrants", self.json())