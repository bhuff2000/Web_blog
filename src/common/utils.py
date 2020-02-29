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
    def get_from_sportradar(type1, year, series):
        key = os.environ.get("SPORTRADAR_KEY")
        conn = http.client.HTTPSConnection("api.sportradar.us")
        url = '/nascar-ot3/' + series + '/' + year + '/' + type1 + '/schedule.json?api_key=' + key
        conn.request("GET", url)
        res = conn.getresponse()
        data = res.read()
        json_file = json.loads(data)
        return json_file
  #      return url

