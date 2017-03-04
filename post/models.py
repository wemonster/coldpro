from flask import current_app,request
from flask_wtf import Form
import wtforms
from datetime import datetime
import time
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from text import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from text import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import hashlib
from text.admin.models import *
import bleach
from markdown import markdownmd



class Post(db.Model):
	__tablename__ = 'posts'
	id = db.Column(db.Integer,primary_key=True)
	body = db.Column(db.String)
	author_id = db.Column(db.Integer,db.ForeignKey('UserData.id'))
	# current_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
	timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow())
	title = db.Column(db.String)
	tags = db.Column(db.String)
	game = db.Column(db.String,nullable=False)
	appreciate = db.Column(db.Integer)
	like = db.relationship('LikePost',backref='post',lazy='dynamic')
	comments = db.relationship('Comment',backref='post',lazy='dynamic')
	repost = db.relationship('Repost',backref='post',lazy='dynamic')
	views = db.Column(db.Integer,default=1)
	sessions = db.Column(db.String)

class Comment(db.Model):
	__tablename__ = 'comment'
	id = db.Column(db.Integer,primary_key=True)
	body = db.Column(db.String)
	# body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
	disabled = db.Column(db.Boolean,default=False)
	appreciate = db.Column(db.Integer)
	like = db.relationship('LikeComment',backref='comment',lazy='dynamic') 
	commenter_id = db.Column(db.Integer,db.ForeignKey('UserData.id'))
	post_id = db.Column(db.Integer,db.ForeignKey('posts.id'))

class LikePost(db.Model):
	__tablename__ = 'like_post'
	id = db.Column(db.Integer,primary_key=True)
	liker_id = db.Column(db.Integer,db.ForeignKey('UserData.id'))
	liked_id = db.Column(db.Integer,db.ForeignKey('posts.id'))
	timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)

class LikeComment(db.Model):
	__tablename__ = 'like_comment'
	id = db.Column(db.Integer,primary_key=True)
	liker_id = db.Column(db.Integer,db.ForeignKey('UserData.id'))
	liked_id = db.Column(db.Integer,db.ForeignKey('comment.id'))
	timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)

class Repost(db.Model):
	__tablename__ = 'repost'
	id = db.Column(db.Integer,primary_key=True)
	repost_comment = db.Column(db.String)
	reposter_id = db.Column(db.Integer,db.ForeignKey('UserData.id'))
	post_id = db.Column(db.Integer,db.ForeignKey('posts.id'))
	timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
# 	@staticmethod
# 	def on_changed_body(target,value,oldvalue,initiator):
# 		allowed_tags = ['a','abbr','acronym','b','code','em','i','strong']
# 		target.body_html = bleach.linkify(bleach.clean(markdown(value,output_format='html'),tags=allowed_tags,strip=True))
# db.event.listen(Comment.body,'set',Comment.on_changed_body)
