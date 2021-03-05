import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash , session, g, json, Blueprint , redirect, request, abort, send_from_directory, jsonify,  Response
from vrecruit import app, db, bcrypt, mail
from vrecruit.forms import (RegistrationForm, DetailsEmployer, DetailsApplicant, LoginForm, UpdateAccountForm,
                             PostJobForm, RequestResetForm, ResetPasswordForm)
from vrecruit.models import User, Employer, Applicant, PostJob
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import numpy as np 
import cv2 
from imutils.video import VideoStream
from collections import deque 
import threading
import argparse
import json
from vrecruit.cv import cv_screen
from subprocess import call
from flask_socketio import SocketIO, join_room

static_folder="static"

cv_screen()

class jd:
    def __init__(self, name):
        self.name = name

def getfilepath(loc):
    temp = str(loc).split('\\')
    return temp[-1]

@app.route("/")
@app.route("/index")
def index():
    return render_template('index/index.html')

@app.route('/for-employer')
def employer_home():
    return render_template('index/employer_home.html', title='For Employer')

@app.route('/for-applicant')
def applicant_home():
    return render_template('index/applicant_home.html', title='For Applicants')

@app.route("/about")
def about():
    return render_template('extra/about.html', title='About')

@app.route('/termsandconditions')
def terms():
    return render_template('extra/terms_of_service.html', title='Terms & Conditions')

@app.route('/privacypolicy')
def privacy():
    return render_template('extra/privacy_policy.html', title='Privacy Policy')

@app.route('/helpcenter')
def help():
    return render_template('extra/help_center.html', title='Help Center')

@app.route('/employer')
@login_required
def employer_index():
    if current_user.user_type == 'Employer':
        page = request.args.get('page', 1, type=int)
        user = User.query.filter_by(email=current_user.email).first_or_404()
        posts = PostJob.query.filter_by(author=user)\
        .order_by(PostJob.date_posted.desc())\
        .paginate(page=page, per_page=5)
        return render_template('dashboard/employer_index.html', title='For Employer', posts=posts, user=user)
    return redirect(url_for('applicant_index'))

@app.route('/applicant')
@login_required
def applicant_index():
    if current_user.user_type == 'Applicant':
       page = request.args.get('page', 1, type=int)
       posts = PostJob.query.order_by(PostJob.date_posted.desc()).paginate(page=page, per_page=5)
       return render_template('dashboard/applicant_index.html', title='For Applicants', posts=posts)
    return redirect(url_for('employer_index'))

@app.route('/interview')
@login_required
def interview_screen():
    if current_user.user_type == 'Applicant':
        return render_template('interview_screen.html', title='Interview')
    return redirect(url_for('index'))

@app.route('/jobposted')
def posted_job():
    page = request.args.get('page', 1, type=int)
    posts = PostJob.query.order_by(PostJob.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('jobposted.html', title='Jobs Posted', posts=posts)

@app.route('/add_details', methods=['GET', 'POST'])
@login_required
def add_details():

    if current_user.new_acc == True:
        if current_user.user_type == 'Employer':
            form = DetailsEmployer()
            if form.validate_on_submit():
                details = Employer(designation=form.designation.data, company_name=form.company_name.data, company_website=form.company_website.data, company_address=form.company_address.data, user_id=current_user.id)
                db.session.add(details)
                current_user.new_acc = False
                db.session.commit()
                flash('Your details have been added!', 'success')
                return redirect(url_for('new_post'))
        else:
            form = DetailsApplicant()
            if form.validate_on_submit():
                details = Applicant(college_name=form.college_name.data, age=form.age.data, user_id=current_user.id)
                db.session.add(details)
                current_user.new_acc = False
                db.session.commit()
                flash('Your details have been added!', 'success')
                return redirect(url_for('applicant_index'))

        return render_template('user/add_details.html', title="Complete Sign Up",form=form)
    
    else:
        if current_user.user_type == 'Employer':
                   return redirect(url_for('employer_index'))
        return redirect(url_for('applicant_index'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.new_acc == False:
            if current_user.user_type == 'Employer':
                return redirect(url_for('employer_index'))
            return redirect(url_for('applicant_index'))   
        return redirect(url_for('add_details'))   

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(your_name=form.your_name.data, contact_number=form.contact_number.data, user_type=form.user_type.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('user/register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        if current_user.new_acc == False:
            if current_user.user_type == 'Employer':
                return redirect(url_for('employer_index'))
            return redirect(url_for('applicant_index'))   
        return redirect(url_for('add_details'))   

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if current_user.new_acc == False:
                if current_user.user_type == 'Employer':
                    return redirect(url_for('employer_index'))
                return redirect(url_for('applicant_index'))   
            return redirect(url_for('add_details'))  
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('user/login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('user/account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():

    if current_user.user_type == 'Employer':
        form = PostJobForm()
        if form.validate_on_submit():
            post = PostJob(job_type=form.job_type.data, no_of_openings=form.no_of_openings.data, job_profile=form.job_profile.data, job_stipend=form.job_stipend.data, job_description=form.job_description.data, skills_required=form.skills_required.data, job_experience=form.job_experience.data, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created!', 'success')
            return redirect(url_for('employer_index'))
        return render_template('create_post.html', title='Post a Job',
                               form=form)
    return redirect(url_for('applicant_index'))   

@app.route("/post/<int:post_id>")
def post(post_id):
    post = PostJob.query.get_or_404(post_id)
    return render_template('post.html', post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = PostJob.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostJobForm()
    if form.validate_on_submit():
        post.job_type=form.job_type.data
        post.no_of_openings=form.no_of_openings.data
        post.job_profile=form.job_profile.data
        post.job_stipend=form.job_stipend.data
        post.job_description=form.job_description.data
        post.skills_required=form.skills_required.data
        post.job_experience=form.job_experience.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.job_type.data=post.job_type
        form.no_of_openings.data=post.no_of_openings
        form.job_profile.data=post.job_profile
        form.job_stipend.data=post.job_stipend
        form.job_description.data=post.job_description
        form.skills_required.data=post.skills_required
        form.job_experience.data=post.job_experience

    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = PostJob.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('employer_index'))


@app.route("/user/<string:email>")
def user_posts(email):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(email=email).first_or_404()
    posts = PostJob.query.filter_by(author=user)\
        .order_by(PostJob.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('employer_index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('user/reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('employer_index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('user/reset_token.html', title='Reset Password', form=form)

