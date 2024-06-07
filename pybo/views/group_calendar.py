from flask import Blueprint, request, jsonify, session, g
from pybo import db
from pybo.models import User, Group, GroupEvent, GroupMember
from datetime import datetime

bp = Blueprint('group', __name__, url_prefix='/group')

@bp.route('/create', methods=['POST'])
def create_group():
    data = request.get_json()
    group_name = data.get('group_name')
    group_code = data.get('group_code')
    user_id = g.user.id  # 현재 로그인한 사용자의 ID를 가져옴

    if not group_name or not group_code:
        return jsonify({'success': False, 'message': '그룹 이름과 그룹 코드를 모두 입력하세요.'}), 400

    if Group.query.filter_by(code=group_code).first():
        return jsonify({'success': False, 'message': '그룹 코드가 이미 존재합니다.'}), 409

    # 그룹 생성 시 그룹을 만든 사용자의 ID를 저장
    group = Group(name=group_name, code=group_code, creator_id=user_id)
    db.session.add(group)
    db.session.commit()

    # 그룹 생성자도 자동으로 그룹 멤버에 추가
    group_member = GroupMember(user_id=user_id, group_id=group.id)
    db.session.add(group_member)
    db.session.commit()

    return jsonify({'success': True, 'message': '그룹이 성공적으로 생성되었습니다.'}), 201

@bp.route('/join', methods=['POST'])
def join_group():
    data = request.get_json()
    group_code = data.get('group_code')
    user_id = g.user.id

    if not group_code:
        return jsonify({'success': False, 'message': '그룹 코드를 입력하세요.'}), 400

    group = Group.query.filter_by(code=group_code).first()
    if not group:
        return jsonify({'success': False, 'message': '유효하지 않은 그룹 코드입니다.'}), 404

    user = User.query.get(user_id)
    existing_member = GroupMember.query.filter_by(user_id=user_id, group_id=group.id).first()
    if existing_member:
        return jsonify({'success': False, 'message': '이미 해당 그룹에 참가하였습니다.'}), 409

    # 그룹 멤버에 사용자 추가
    group_member = GroupMember(user_id=user_id, group_id=group.id)
    db.session.add(group_member)
    db.session.commit()

    return jsonify({'success': True, 'message': '성공적으로 그룹에 참가하였습니다.'}), 200


@bp.route('/add_event', methods=['POST'])
def add_group_event():
    data = request.get_json()
    description = data['description']
    date = data['date']
    user_id = g.user.id

    # 사용자가 속한 그룹의 ID를 디버깅 메시지로 출력
    print("User's group memberships:", g.user.group_memberships)

    # 사용자가 속한 모든 그룹의 ID를 리스트로 저장
    group_ids = [membership.group_id for membership in g.user.group_memberships]
    print("User's group IDs:", group_ids)

    # 선택된 그룹 ID를 디버깅 메시지로 출력
    selected_group_id = group_ids[0] if group_ids else None
    print("Selected group ID:", selected_group_id)

    event = GroupEvent(description=description, date=datetime.strptime(date, '%Y-%m-%d'), user_id=user_id,
                       group_id=selected_group_id)
    db.session.add(event)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Event added successfully'})


@bp.route('/get_events', methods=['GET'])
def get_group_events():
    date = request.args.get('date')
    user_id = g.user.id

    # 사용자가 속한 그룹들의 ID 가져오기
    group_ids = [membership.group_id for membership in g.user.group_memberships]

    # 해당 날짜에 그룹 멤버인 사용자의 이벤트들을 가져오기
    events = GroupEvent.query.filter(GroupEvent.date == datetime.strptime(date, '%Y-%m-%d'),
                                     GroupEvent.group_id.in_(group_ids)).all()
    events_list = [{'description': event.description, 'date': event.date.isoformat()} for event in events]

    return jsonify({'events': events_list})


@bp.route('/delete_event', methods=['POST'])
def delete_group_event():
    data = request.get_json()
    description = data['description']
    date = data['date']
    user_id = g.user.id
    group_id = g.user.group_id

    event = GroupEvent.query.filter_by(description=description, date=datetime.strptime(date, '%Y-%m-%d'), user_id=user_id, group_id=group_id).first()
    if event:
        db.session.delete(event)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Event deleted successfully'})
    return jsonify({'success': False, 'message': 'Event not found'})
