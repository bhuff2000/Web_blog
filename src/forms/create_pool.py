__author__ = 'behou'


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, email, Regexp


class CreatePool(FlaskForm):
    pool_name = StringField('pool_name', validators=[DataRequired(), Length(1, 64),
                Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                'Pool Name must have only letters, numbers, dots or underscores')])
    members = StringField('members', validators=[DataRequired(), Length(1, 64),
                Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                'Usernames must have only letters, numbers, dots or underscores')])
    submit = SubmitField('Create Pool')