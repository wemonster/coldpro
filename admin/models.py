from flask import current_app,request
from flask_wtf import Form
import wtforms
from datetime import datetime
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from text import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from text import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import hashlib
from text.post.models import *

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer,db.ForeignKey('UserData.id'),primary_key=True)
    followed_id = db.Column(db.Integer,db.ForeignKey('UserData.id'),primary_key=True)
    timestamp = db.Column(db.DateTime,default=datetime.utcnow)

class UserData(UserMixin,db.Model):
    def __init__(self,**kwargs):
        super(UserData,self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter(Role.permission==0xff).first()
            else:
                self.role = Role.query.filter(Role.default==True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf8')).hexdigest()
            db.session.add(self)
            db.session.commit()

    def gravatar(self,size=100,default='identicon',rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        if self.avatar is not None:
            return self.avatar
        else:
            self.avatar_hash = hashlib.md5(self.email.encode('utf8')).hexdigest()
            hash = self.avatar_hash
            return '{}/{}?s={}&d={}&r={}'.format(url,hash,size,default,rating)

    __tablename__ = 'UserData'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String,unique=True)
    nickname = db.Column(db.String,unique=True)
    password = db.Column(db.String)
    repeat = db.Column(db.String)
    email = db.Column(db.String)
    agree = db.Column(db.Boolean,default=False)
    registered_date = db.Column(db.DateTime,default=datetime.now())
    confirmed = db.Column(db.Boolean,default=False)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    about_me = db.Column(db.Text)
    last_seen = db.Column(db.DateTime,default=datetime.utcnow)
    avatar_hash = db.Column(db.String)
    avatar = db.Column(db.String)
    posts = db.relationship('Post',backref='author',lazy='dynamic')
    appreciate = db.Column(db.Integer)
    likepost = db.relationship('LikePost',backref='liker',lazy='dynamic')
    likecomment = db.relationship('LikeComment',backref='liker',lazy='dynamic')
    followed = db.relationship('Follow',foreign_keys=[Follow.follower_id],
        backref=db.backref('follower',lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan')
    followers = db.relationship('Follow',foreign_keys=[Follow.followed_id],
        backref=db.backref('followed',lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan')
    comments = db.relationship('Comment',backref='commenter',lazy='dynamic')
    repost = db.relationship('Repost',backref='reposter',lazy='dynamic')
    def repost_post(self,post,comment):
        repost = Repost(reposter=self,post=post,repost_comment=comment)
        db.session.add(repost)
        db.session.commit()

    def delete_repost(self,post):
        post = self.repost.filter_by(post_id=post.id).first()
        if post:
            db.session.delete(post)
            db.session.commit()
            
    def like_post(self,post):
        if not self.has_liked_post(post):
            l = LikePost(post=post,liker=self)
            db.session.add(l)
            db.session.commit()

    def unlike_post(self,post):
        l = self.likepost.filter_by(liked_id=post.id).first()
        if l:
            db.session.delete(l)
            db.session.commit()

    def has_liked_post(self,post):
        return self.likepost.filter_by(liked_id=post.id).first() is not None

    def like_comment(self,comment):
        if not self.has_liked_comment(comment):
            c = LikeComment(liker=self,comment=comment)
            db.session.add(c)
            db.session.commit()

    def unlike_comment(self,comment):
        c = self.likecomment.filter_by(liked_id=comment.id).first()
        if c:
            db.session.delete(c)
            db.session.commit()

    def has_liked_comment(self,comment):
        return self.likecomment.filter_by(liked_id=comment.id).first() is not None

    def follow(self,user):
        if not self.is_following(user):
            f = Follow(follower=self,followed=user)
            db.session.add(f)
            db.session.commit()

    def unfollow(self,user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following(self,user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self,user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def can(self,permission):
        return self.role is not None and (self.role.permission&permission) == permission

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
    
    @property
    def password_test(self):
        raise AttributeError('password is not a readable attribute')

    @password_test.setter
    def password_test(self,password):
        self.password = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password,password)
    
    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirmed':self.id})

    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        # try:
        data = s.loads(token)
        return data
        # except:
        #     return False
        # if data.get('confirmed') != self.id:
        #     return False
        # self.confirmed = True
        # db.session.add(self)
        # db.session.commit()
        # return True
    def __repr__(self):
        return '<User {}:{}>'.format(self.username,self.email)

class AnonymousUser(AnonymousUserMixin):
    def can(self,permission):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String,unique=True)
    default = db.Column(db.Boolean,default=False,index=True)
    permission = db.Column(db.Integer)
    users = db.relationship('UserData',backref='role',lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User':(Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES,True),
            'Moderator':(Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS,False),
            'Administrator':(0xff,False)
        }
        for r in roles:
            role = Role.query.filter(Role.username==r).first()
            if role is None:
                role = Role(username=r)
            role.permission = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role {}>'.format(self.username)


@login_manager.user_loader
def load_user(user_id):
    return UserData.query.get(user_id)

