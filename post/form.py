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



class PostForm(Form):
	body = wtforms.FileField('video')
	tags = wtforms.StringField('tags')
	title = wtforms.StringField('title',validators=[Required()])
	game = wtforms.SelectField('game',choices=[('csgo','Counter Strike: Global Offensive'),('ow','Overwatch'),('lol','League of Legende'),('dota2','dota2'),('hs','hearthstone')],validators=[Required()])


class CommentForm(Form):
	body = wtforms.TextAreaField('body',validators=[Required()])

class RepostForm(Form):
	body = wtforms.StringField('comment')
