from flask import Blueprint, url_for, render_template
from werkzeug.utils import redirect

bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/cal/')
def cal():                                  #학과캘린더
    return render_template('cal.html')


@bp.route('/')
def index():                                #메인페이지
    return render_template('main.html')

@bp.route('/group_create/')
def group_create():                                  #학과캘린더
    return render_template('group_create.html')


@bp.route('/group_join/')
def group_join():                                  #학과캘린더
    return render_template('group_join.html')

@bp.route('/group_calendar/')
def group_calendar():                                  #학과캘린더
    return render_template('group_calendar.html')
