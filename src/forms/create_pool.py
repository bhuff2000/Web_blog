__author__ = 'behou'


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, email, Regexp
from src.models.rooms import Room



class CreatePool(FlaskForm):
    pool_name = StringField('Pool Name', validators=[DataRequired(), Length(1, 64),
                Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                'Pool Name must have only letters, numbers, dots or underscores')])
    #members = StringField('Members', validators=[DataRequired(), Length(1, 64),
    #            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
    #            'Usernames must have only letters, numbers, dots or underscores')])
    members = StringField('Members', validators=[DataRequired(), Length(1, 64)])
    series = SelectField('Select Series', choices=[('Choose Series', 'Choose Series'), ('go', 'TRUCKS'), ('xf','XFINITY'), ('sc', 'CUP')])
    race = SelectField('Select Race', choices=[('Choose_race', 'Choose Race')], validate_choice=False)
    submit = SubmitField('Create Pool')

    @classmethod
    def already_exists(cls, room_name, username):
        room_exists = Room.find_by_roomname_and_username(room_name, username)
        if room_exists is not None:
            room_list = {}
            #for room in room_exists:
                #code not complete, idea is this will provide list of pools for a user
