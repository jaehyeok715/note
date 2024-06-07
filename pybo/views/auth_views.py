from flask import (Blueprint, url_for, render_template,
                   flash, request, session, g, jsonify)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from datetime import datetime
from pybo import db
from pybo.forms import UserCreateForm, UserLoginForm, UserSchoolForm, UserMajorForm
from pybo.models import User, Event

local_date_string = "2024-05-29T12:00:00.000Z"  # 클라이언트로부터 전송된 예시 날짜 문자열
local_datetime = datetime.fromisoformat(local_date_string)  # 클라이언트의 로컬 시간대로 변환된 datetime 객체
print(local_datetime)

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = UserCreateForm()

    if form.validate_on_submit():
        username = form.username.data
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('이미 존재하는 사용자입니다.')
            return redirect(url_for('auth.signup'))  # 회원가입 페이지로 리다이렉트

        email = form.email.data
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('이미 사용 중인 이메일 주소입니다.')
            return redirect(url_for('auth.signup'))  # 회원가입 페이지로 리다이렉트

        session['username'] = username
        session['email'] = email
        session['password'] = form.password1.data  # 패스워드 세션에 저장
        session['step'] = 2  # 다음 단계로 이동

        return redirect(url_for('auth.signup_step2'))

    return render_template('auth/signup.html', form=form)



@bp.route('/signup/step2/', methods=['GET', 'POST'])
def signup_step2():
    if 'step' not in session or session['step'] != 2:
        return redirect(url_for('auth.signup'))  # 첫 번째 단계로 리다이렉트

    form = UserSchoolForm()

    if form.validate_on_submit():
        session['school'] = form.school.data
        session['step'] = 3  # 다음 단계로 이동

        return redirect(url_for('auth.signup_step3'))

    return render_template('auth/signup_step2.html', form=form)


@bp.route('/signup/step3/', methods=['GET', 'POST'])
def signup_step3():
    if 'step' not in session or session['step'] != 3:
        return redirect(url_for('auth.signup'))  # 첫 번째 단계로 리다이렉트

    form = UserMajorForm()

    if form.validate_on_submit():
        session['major'] = form.major.data
        # 여기서 세션에 저장된 정보를 사용하여 회원가입 처리를 합니다.

        # 데이터베이스에 사용자 정보 저장
        username = session['username']
        email = session['email']
        password = session['password']
        major = session['major']
        school = session['school']

        hashed_password = generate_password_hash(password)

        # 사용자 정보 저장
        user = User(username=username, email=email, password=hashed_password, major=major, school=school)
        db.session.add(user)
        db.session.commit()

        session.clear()  # 회원가입이 완료되면 세션 초기화
        return redirect(url_for('auth.login'))

    return render_template('auth/signup_step3.html', form=form)

@bp.route('/login/', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        error = None
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            error = "존재하지 않는 사용자입니다."
        elif not check_password_hash(user.password, form.password.data):
            error = "비밀번호가 올바르지 않습니다."
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('main.index'))
        flash(error)
    return render_template('auth/login.html', form=form)

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)


@bp.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

@bp.route('/add_event/', methods=['POST'])
def add_event():
    description = request.json.get('description')
    date = request.json.get('date')

    if description and date:
        if g.user:
            event_date = datetime.strptime(date, '%Y-%m-%d').date()
            event = Event(description=description, date=event_date, user_id=g.user.id)
            db.session.add(event)
            db.session.commit()
            return jsonify({'success': True, 'message': '일정이 추가되었습니다.'}), 200
        else:
            return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    else:
        return jsonify({'success': False, 'message': '일정 정보가 유효하지 않습니다.'}), 400

@bp.route('/get_events/', methods=['GET'])
def get_events():
    date = request.args.get('date')

    if date:
        event_date = datetime.strptime(date, '%Y-%m-%d').date()
        events = Event.query.filter_by(user_id=g.user.id, date=event_date).all()
        events_data = [{'description': event.description, 'date': event.date.isoformat()} for event in events]
        return jsonify({'events': events_data}), 200
    else:
        return jsonify({'success': False, 'message': '날짜 정보가 유효하지 않습니다.'}), 400



@bp.route('/delete_event/', methods=['POST'])
def delete_event():
    if not g.user:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401

    description = request.json.get('description')
    date = request.json.get('date')

    if description and date:
        try:
            event_date = datetime.strptime(date, '%Y-%m-%d').date()
            event = Event.query.filter_by(user_id=g.user.id, description=description, date=event_date).first()
            if event:
                db.session.delete(event)
                db.session.commit()
                return jsonify({'success': True, 'message': '일정이 삭제되었습니다.'}), 200
            else:
                return jsonify({'success': False, 'message': '일정을 찾을 수 없습니다.'}), 404
        except ValueError:
            return jsonify({'success': False, 'message': '날짜 형식이 유효하지 않습니다.'}), 400
    else:
        return jsonify({'success': False, 'message': '일정 정보가 유효하지 않습니다.'}), 400