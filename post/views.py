from flask import Blueprint, render_template, url_for, request, redirect, flash,jsonify,session,abort,make_response
from werkzeug import secure_filename
from text import db, app,mail
import datetime
import json
from text.admin.models import *
from flask_login import login_user,login_required,logout_user,current_user
from text.admin import admin
from flask_mail import Message
from threading import Thread
from text.admin.form import *
import os
from text.post.form import *
from text.post.models import *

post = Blueprint('post',__name__)

@post.route('/<id>',methods=['GET','POST'])
def get_video(id):
    post = Post.query.filter(Post.id==id).first()
    form_comm = CommentForm()
    form_repost = RepostForm()
    # all_viewer = post.sessions
    # origin = []
    # if post.sessions:
    #     all_viewer = [].append(post.sessions)
    # else:
    #     all_viewer = []
    # session = request.cookies.get('session')
    # if session not in all_viewer:
    #     post.views +=1     
    #     all_viewer.append(session)
    post.views += 1
    db.session.add(post)
    db.session.commit()
    # post.views += 1          
    return render_template('html/videos.html',posts=post,form_comm=form_comm,form_repo=form_repost)

@post.route('/lol/')
def get_lol_subpage():  
    post = Post.query.filter(Post.game=='lol').all()
    page = request.args.get('page',1,type=int)
    pagination = Post.query.filter_by(game='lol').order_by(Post.timestamp.desc()).paginate(page,per_page=app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
    post = pagination.items
    return render_template('posts/lolsubpage.html',posts=post,pagination=pagination)

@post.route('/dota2/')
def get_dota2_subpage():
    page = request.args.get('page',1,type=int)
    pagination = Post.query.filter_by(game='dota2').order_by(Post.timestamp.desc()).paginate(page,per_page=app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
    post = pagination.items
    return render_template('posts/dota2subpage.html',posts=post,pagination=pagination)

@post.route('/csgo/')
def get_csgo_subpage():
    page = request.args.get('page',1,type=int)
    pagination = Post.query.filter_by(game='csgo').order_by(Post.timestamp.desc()).paginate(page,per_page=app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
    post = pagination.items
    return render_template('posts/csgosubpage.html',posts=post,pagination=pagination)

@post.route('/hearthstone/')
def get_hs_subpage():
    page = request.args.get('page',1,type=int)
    pagination = Post.query.filter_by(game='hs').order_by(Post.timestamp.desc()).paginate(page,per_page=app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
    post = pagination.items
    return render_template('posts/hearthstonesubpage.html',posts=post,pagination=pagination)

@post.route('/overwatch/')
def get_ow_subpage():
    page = request.args.get('page',1,type=int)
    pagination = Post.query.filter_by(game='ow').order_by(Post.timestamp.desc()).paginate(page,per_page=app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
    post = pagination.items
    return render_template('posts/overwatchsubpage.html',posts=post,pagination=pagination)


@post.route('/uploads/')
@login_required
def uploads():
    form = PostForm()
    return render_template('html/users/uploads.html',form=form)

@post.route('/uploading/',methods=['GET','POST'])
@login_required
def upload_progress():
    user = current_user._get_current_object()
    path = app.config['UPLOAD_FOLDER_VIDEO'] + str(user.nickname)
    if request.method == 'POST':
        file = request.files['video']
        filename = secure_filename(file.filename)
        if not os.path.exists(path):
            os.makedirs(path)
        file.save(os.path.join(path,filename))
        flash('文件上传成功')
    return True
    # filename = secure_filename(file.name)
    # if not os.path.exists(path):
    #     os.makedirs(path)
    # file.save(os.path.join(path,filename))
    # return True
@post.route('/cancelupload/')
@login_required
def check_uploads():
    user = current_user._get_current_object()
    path = app.config['UPLOAD_FOLDER_VIDEO'] + str(user.nickname)
    result = {'msg':True}
    result = request.args.get('exist')
    filename = secure_filename(request.args.get('filename'))
    if result == 'yes':
        os.remove(os.path.join(path,filename))
    else:
        result = {'msg':False}
    return jsonify(result)

@post.route('/submit-uploads/',methods=['GET','POST'])
@login_required
def submit_uploads():
    form = PostForm()
    if form.validate_on_submit:
        body = request.files['upload-video']
        author = current_user._get_current_object()
        user = UserData.query.filter(UserData.id == author.id).first()
        nickname = user.nickname
        filename = secure_filename(body.filename)
        body = '/static/uploads/video/' + str(nickname) + '/' + str(filename)
        tags = form.tags.data
        post = Post(body=body,title=form.title.data,tags=tags,author=author,game=form.game.data)
        db.session.add(post)
        db.session.commit()
        flash('you have uploaded a video','upload')
        return redirect(url_for('post.uploads',form=form))
    # return render_template('html/users/uploads.html',form=form)

@post.route('/comment/<int:id>',methods=['GET','POST'])
@login_required
def comment(id):
    post = Post.query.filter_by(id=id).first()
    form = CommentForm()
    if form.validate_on_submit:
        comment = Comment(
            body=form.body.data,
            post=post,
            commenter=current_user._get_current_object()
            )
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('post.get_video',id=post.id))
    return render_template('html/videos.html',form=form,posts=post)

@post.route('/comment/delete/<int:id>',methods=['GET','POST'])
@login_required
def delete_comment(id):
    comment = Comment.query.filter_by(id=id).first()
    form = CommentForm()
    post = Post.query.filter_by(id=comment.post.id).first()
    if comment:
        db.session.delete(comment)
        db.session.commit()
        return redirect(url_for('post.get_video',id=post.id))
    return render_template('html/videos.html',form=form,posts=post)

@post.route('/like/',methods=['GET','POST'])
@login_required
def like_post():
    id = request.args.get('id')
    post = Post.query.filter_by(id=id).first()
    result = {'like':True}
    if current_user.has_liked_post(post):
        current_user.unlike_post(post)
        result = {'like':False}
        return jsonify(result)
    else:
        current_user.like_post(post)
        return jsonify(result)

@post.route('/comment/like/',methods=['GET','POST'])
@login_required
def like_comment():
    id = request.args.get('id')
    comment = Comment.query.filter_by(id=id).first()
    result = {'like':True}
    if current_user.has_liked_comment(comment):
        current_user.unlike_comment(comment)
        result = {'like':False}
        return jsonify(result)
    else:
        current_user.like_comment(comment)
        return jsonify(result)


@post.route('/repost/<int:id>',methods=['GET','POST'])
@login_required
def repost(id):
    form = RepostForm()
    post = Post.query.filter_by(id=id).first()
    comment = form.body.data
    current_user.repost_post(post,comment)
    return redirect(url_for('post.get_video',id=id,form=form))
    # return jsonify({'repost':True})

@post.route('/repost/delete/<int:id>',methods=['GET','POST'])
@login_required
def repost_delete(id):
    repost = Repost.query.filter_by(id=id).first()
    user = current_user._get_current_object()
    reposts = Repost.query.filter_by(reposter_id=user.id).all() 
    if repost:
        db.session.delete(repost)
        db.session.commit()
    return redirect(url_for('admin.user_page',user=user,reposts=reposts,username=user.username))
    # current_user.delete_repost(post)
    # return jsonify({'delete':True})

