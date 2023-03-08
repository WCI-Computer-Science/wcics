from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, session
from flask_login import current_user, login_required
from app import db
from app.models import User, Attendance
import json

bp = Blueprint('account', __name__)

@bp.route('/')
@login_required
def home():
    return render_template('account/home.html', user=current_user)

