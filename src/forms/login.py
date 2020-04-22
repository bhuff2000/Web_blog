__author__ = 'behou'

from flask_wtf import FlaskForm, form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length
from email_validator import validate_email

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[validate_email,  DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')
