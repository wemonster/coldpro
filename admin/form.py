from flask import current_app
from flask_wtf import Form
import wtforms
from datetime import datetime
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from text import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin, current_user
from text import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer



class LoginForm(Form):
    username = wtforms.StringField('Email/Username',validators=[Required()])
    password = wtforms.PasswordField('Password')
    submit = wtforms.SubmitField('submit')

class SignupForm(Form):
    username = wtforms.StringField('Username',validators=[Required()])
    password = wtforms.PasswordField('Password',validators=[Required(),EqualTo('repeat',message='password does not match')])
    repeat = wtforms.PasswordField('Confirm',validators=[Required()])
    email = wtforms.StringField('Email',validators=[Required(),Email()])
    nickname = wtforms.StringField('Nickname',validators=[Required()])
    agree = wtforms.BooleanField('Agree',validators=[Required()])
    submit = wtforms.SubmitField('submit')
    def validate_email(self,field):
        if UserData.query.filter_by(email = field.data).first():
            raise ValitationError('Email already registered')

    def validate_username(self,field):
        if UserData.query.filter_by(username=field.data).first():
            raise ValitationError('Username already registered')

class EditProfileForm(Form):
    nickname = wtforms.StringField('nickname',validators=[Length(0,32)])
    password = wtforms.PasswordField('password',validators=[Length(0,32)])
    confirm = wtforms.PasswordField('password',validators=[Length(0,32)])
    about_me = wtforms.TextAreaField('about me')
    username = wtforms.StringField('nickname',validators=[Length(0,32)])
    email = wtforms.StringField('email',validators=[Email()])
