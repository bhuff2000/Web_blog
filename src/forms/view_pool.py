__author__ = 'behou'


from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired, Length, email, Regexp
from src.models.rooms import Room
from src.models.races import Sched_Event
from bson import ObjectId
import wtforms
from wtforms_validators import Email



class DriverList(FlaskForm):
    driver = SelectField('driver list', validators=None, validate_choice=False)


    @classmethod
    def add_choices(cls, mongo_list):
        #print('driver' + str(mongo_list))
        #drivers_list = [(driver['car_num']) for driver in mongo_list]
        #print(drivers_list)
        cls.driver.choices = [(driver['car_num'] + ' - ' + driver['drv_full'] ) for driver in mongo_list]


class SelectDriver(FlaskForm):

    driver_list = wtforms.FormField(DriverList)
    #choose_driver = SubmitField('Choose Driver')


    #@classmethod
    #def already_exists(cls, room_name, username):
    #    room_exists = Room.find_by_roomname_and_username(room_name, username)
    #    if room_exists is not None:
    #        room_list = {}


