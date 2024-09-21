from flask import Blueprint, redirect, render_template, url_for, session, flash, request
from werkzeug.urls import url_parse
from app import app, db
from app.oauth import get_auth_url, get_access_token, get_user_info
from app.models import User
from flask_login import current_user, login_user, logout_user

bp = Blueprint('auth', __name__)


@bp.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    session['next'] = request.args.get('next')
    return render_template('auth/login.html')

@bp.route('/auth/google')
def authorize():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return redirect(get_auth_url())

@bp.route('/auth/callback')
def callback():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    access_token = get_access_token()
    if access_token == 'error':
        flash("Invalid credentials. Please try again.", "error")
        return redirect(url_for('auth.login'))
    
    user_info = get_user_info(access_token)
    user_email = user_info['email']
    user = User.query.filter_by(email=user_email).first()
    if user_email.split('@')[1] != "wrdsb.ca" and user_email != app.config['ADMIN_EMAIL']:
        flash("Please login with your school account.")
        return redirect(url_for('auth.login'))
    
    if not user:
        user = User(first_name=user_info['given_name'], 
                    last_name=user_info['family_name'], 
                    email=user_email)
        db.session.add(user)
        db.session.commit()

    login_user(user, remember=True)
    next_page = session.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('main.index')
    session.pop('next', None)
    return redirect(next_page)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))