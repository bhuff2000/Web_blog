__author__ = 'behou'

from passlib.hash import pbkdf2_sha512
import re
import http.client
import json
import os

class Utils:
    @staticmethod
    def email_is_vaild(email: str) -> bool:
        email_address_matcher = re.compile(r'^[\w-]+@([\w-]+\.)+[\w]+$')
        return True if email_address_matcher(email) else False

    @staticmethod
    def hash_password(password: str) -> str:
        return pbkdf2_sha512.encrypt(password)

    @staticmethod
    def check_hashed_password(password: str, hashed_password: str) -> bool:
        return pbkdf2_sha512.verify(password, hashed_password)

    @staticmethod
    def get_from_sportradar():
        key = os.environ.get("SPORTRADAR_KEY")
        conn = http.client.HTTPSConnection("api.sportradar.us")
        conn.request("GET", "/nascar-ot3/sc/2014/races/schedule.json?api_key=key")
        res = conn.getresponse()
        data = res.read()
        tracks = json.loads(data)
        return tracks

