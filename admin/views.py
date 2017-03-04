from flask import Blueprint, render_template, url_for, request, redirect, flash,jsonify,session,abort
from werkzeug import secure_filename
from text import db, app,mail
from datetime import datetime
import json
from text.admin.models import *
from flask_login import login_user,login_required,logout_user,current_user
from text.admin import admin
from flask_mail import Message
from threading import Thread
from text.admin.form import *
import os
from text.post.models import *
# import Imagepy
ALLOWED_IMG_EXTENTIONS = set(['jpg','png','jpeg','JPG','PNG','JPEG'])


@admin.route('/')
def index():
    return render_template('html/home-page.html')


@admin.route('/mail-test/',methods=['GET','POST'])
def mail_test():
    form = SignupForm(request.form)
    if form.validate_on_submit:
        user = UserData.query.filter(UserData.username==form.username.data).first()
        if user is None:
            user = UserData(username=form.username.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_mail(app.config['FLASKY_ADMIN'],'New User','html/panel1')
        else:
            session['known'] = True
        session['username'] = form.username.data
        form.username.data = ''
        return redirect(url_for('admin.mail_test'))
    return render_template('html/panel2.html',form=form)

def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

def send_mail(to,subject,template,**kwargs):
    mas = Message(
        app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[to])
    mas.body = render_template(template + '.txt', **kwargs)
    mas.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email,args=[app,mas])
    thr.start()

@admin.route('/login/')
def login():
    form = LoginForm(request.form)
    if request.cookies.get('remember_token'):
        return redirect(url_for('admin.index'))
    return render_template('html/panel1.html', form=form)

@admin.route('/login-required/')
def login_require():
    form = LoginForm(request.form)
    if request.cookies.get('remember_token'):
        return redirect(url_for('admin.index'))
    return render_template('html/login-view.html',form=form)

@admin.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.index'))

@admin.route('/validate/',methods=['GET','POST'])
def user_validate():
    result = {'msg':False}
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = UserData.query.filter(UserData.username==username).first()
        if user is not None and user.password == password:
            result = {'msg':True}
    return jsonify(result)


@admin.route('/submit-login/', methods=['GET', 'POST'])
def submit_login():
    form = LoginForm()
    if form.validate_on_submit:
        User = UserData.query.filter(UserData.username==form.username.data).first()
        if User is not None and User.password == form.password.data:
            login_user(User,True)
            return redirect(url_for('admin.user_page',username=current_user.username))
    return redirect(url_for('admin.index'))    


@admin.route('/signup/')
def signup():
    form = SignupForm(request.form)
    return render_template('html/panel2.html', form=form)


@admin.route('/submit-signup/', methods=['GET', 'POST'])
def submit_signup():
    form = SignupForm()
    if form.validate_on_submit:  
        User = UserData(email=form.email.data, username=form.username.data,
                        password=form.password.data, repeat=form.repeat.data, agree=form.agree.data,registered_date=datetime.now())
         #user = UserData.query.filter(UserData.username==form.username.data).first()
        login_user(User,True)
        token = User.generate_confirmation_token()
        send_mail(app.config['FLASKY_ADMIN'],'New User','admin/mail/new_user',User=User)
        send_mail(form.email.data,'Welcome','admin/mail/verify',user=User,token=token)       
        db.session.add(User)
        db.session.commit()
        return redirect(url_for('admin.index'))
    return 'not ok'

@admin.route('/reconfirm/')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_mail(current_user.email,'Confirm your account','admin/mail/verify',user=current_user,token=token)
    return redirect(url_for('admin.index'))

@admin.route('/confirm/<token>')
@login_required
def confirm(token):
    # data = 
    # data = Serializer(current_app.config['SECRET_KEY']).loads('eyJhbGciOiJIUzI1NiIsImlhdCI6MTQ3MzE1ODE4NSwiZXhwIjoxNDczMTYxNzg1fQ.eyJjb25maXJtIjpudWxsfQ.hEcIdh1hfXdT7oCN_OdXnJbdtWU6T4Jsdfc-8iMR1Vo')
    # return token
    # user_id = data['confirm']
    # user = UserData.query.filter(UserData.id==user_id).first()
    # user.confirmed = True
    if current_user.confirmed:
        return redirect(url_for('admin.index'))
    if current_user.confirm(token):
        flash( 'You have confirmed your email address')
        return redirect(url_for('admin.index'))
    else:
        flash('The confirmation link is invalid or has expired')
    return 'jump'
    return redirect(url_for('admin.index'))

@admin.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()

@admin.route('/unconfirmed/')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('admin.index'))
    return render_template('admin/mail/unconfirmed.html',user=current_user)

@admin.route('/checkname/')
def checkname():
    username = request.args.get('username')
    users = UserData.query.filter(UserData.username==username).first()
    result = {'msg':True}
    if users is not None and username == users.username:
        result = {'msg':False}
    elif users is None:
        result = {'msg':True}
    return jsonify(result)

@admin.route('/check-nickname/')
def nickname():
    nickname = request.args.get('nickname')
    users = UserData.query.filter(UserData.nickname==nickname).first()
    result = {'msg':True}
    if users is not None and nickname == users.nickname:
        result = {'msg':False}
    elif users is None:
        result = {'msg':True}
    return jsonify(result)


@admin.route('/user/<username>')
@login_required
def user_page(username):
    user = UserData.query.filter(UserData.username==username).first()
    repost = Repost.query.filter_by(reposter_id=user.id).all()
    if user is None:
        abort(404)
    return render_template('html/users/profile.html',user=user,reposts=repost)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_IMG_EXTENTIONS


@admin.route('/edit-profile/',methods=['GET','POST'])
@login_required
def edit_profile():
    user = UserData.query.filter(UserData.id == current_user.id).first()
    if request.method == 'POST':
        file = request.files['useravatar']
        # im = Image.open(file)
        # size = (50,50)
        # im.thumbnail(size)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = app.config['UPLOAD_FOLDER_IMG'] + str(user.nickname)
            if not os.path.exists(path):
                os.makedirs(path)
            file.save(os.path.join(path,filename))
            user.avatar = '/static/uploads/img/'+ str(user.nickname) + '/' + str(filename)
        user.nickname = request.form.get('nickname')
        user.about_me = request.form.get('about_me')
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.password = request.form.get('password')
        user.repeat = request.form.get('repeat')
        db.session.add(user)
        db.session.commit()
        flash('Your profile has been updated','update')
        return redirect(url_for('admin.edit_profile'))
    return render_template('html/users/edit-profile.html')

@admin.route('/favourite/')
@login_required
def favourite():
    return render_template('html/users/favourite.html')

@admin.route('/user-games/')
@login_required
def user_games():
    return render_template('html/users/games.html')

@admin.route('/history/')
@login_required
def user_history():
    return render_template('html/users/history.html')

@admin.route('/user-uploaded/')
@login_required
def user_upload():
    user = current_user._get_current_object()
    User = UserData.query.filter(UserData.nickname == user.nickname).first()
    page = request.args.get('page',1,type=int)
    posts = User.posts.order_by(Post.timestamp.desc()).paginate(page,per_page=app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
    # post = posts.items
    post = User.posts.order_by(Post.timestamp.desc()).all()
    l = []
    for i in post:
        l.append(i.id)
    return jsonify(l)
    # return render_template('html/users/uploaded.html',user=user,posts=post)

@admin.route('/userpage/<username>')
def outside_page(username):
    user = UserData.query.filter_by(username=username).first()
    return render_template('/html/users/outside-profile.html',user=user,permission=Permission)

@admin.route('/follow/',methods=['GET','POST'])
@login_required
# @permission_required(Permission.FOLLOW)
def follow():
    nickname = request.args.get('nickname')    
    user = UserData.query.filter_by(nickname=nickname).first()
    result = {'msg':True}
    if user is None:
        flash('invalid user')
        # return redirect(url_for('admin.index'))
        result = {'msg':False}
        return jsonify(result)
    if current_user.is_following(user):
        flash('you have already following this user')
        current_user.unfollow(user)
        result = {'msg':False}
        return jsonify(result)
        # return redirect(url_for('admin.outside_page',username=username))
    else:
        current_user.follow(user)
        flash('you have now following {}'.format(nickname))
        return jsonify(result)
    # return redirect(url_for('admin.outside_page',username=username))

@admin.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = UserData.query.filter_by(username=username).first()
    current_user.unfollow(user)
    return redirect(url_for('admin.outside_page',username=username))


@admin.route('/followers/<username>')
@login_required
def my_followers(username):
    user = UserData.query.filter_by(username=username).first()
    page = request.args.get('page',1,type=int)
    pagination = user.followers.paginate(page,per_page=app.config['FLASKY_FOLLOWERS_PER_PAGE'],error_out=False)
    return render_template('html/users/followers.html',pagination=pagination,user=user)

@admin.route('/followed/<username>')
@login_required
def my_followed(username):
    user = UserData.query.filter_by(username=username).first()
    page = request.args.get('page',1,type=int)
    pagination = user.followed.paginate(page,per_page=app.config['FLASKY_FOLLOWERS_PER_PAGE'],error_out=False)
    return render_template('html/users/followed.html',pagination=pagination,user=user)

@admin.route('/<username>/following')
@login_required
def his_followed(username):
    user = UserData.query.filter_by(username=username).first()
    page = request.args.get('page',1,type=int)
    pagination = user.followed.paginate(page,per_page=app.config['FLASKY_FOLLOWERS_PER_PAGE'],error_out=False)
    return render_template('html/users/share-followed.html',pagination=pagination,user=user)

@admin.route('/<username>/follower')
@login_required
def his_follower(username):
    user = UserData.query.filter_by(username=username).first()
    page = request.args.get('page',1,type=int)
    pagination = user.followers.paginate(page,per_page=app.config['FLASKY_FOLLOWERS_PER_PAGE'],error_out=False)
    return render_template('html/users/share-followers.html',pagination=pagination,user=user)