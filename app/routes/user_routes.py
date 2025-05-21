from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_jwt_extended import create_access_token  

from ..models.user import User
from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os

user_bp = Blueprint('user', __name__)



@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid username or password'}), 400

    access_token = create_access_token(identity=str(user.id),expires_delta=datetime.timedelta(days=1000))

    # Lấy thông tin từ user_info nếu có
    user_info = user.user_info
    info_dict = {
        'id': user_info.id,
        'username': user.username,
        'full_name': user_info.full_name if user_info else None,
        'code': user_info.code if user_info else None,
        'gender': user_info.gender if user_info else None,
        'job': user_info.job if user_info else None,
        'phone_number': user_info.phone_number if user_info else None,
        'address': user_info.address if user_info else None,
        'start_date': user_info.start_date.isoformat() if user_info and user_info.start_date else None,
        'last_online': user_info.last_online.isoformat() if user_info and user_info.last_online else None,
        'is_admin': user_info.is_admin if user_info else False,
        'vip': user_info.vip if user_info else False,
        'enabled': user_info.enabled if user_info else True,
    }

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': info_dict
    }), 200


@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Kiểm tra username hoặc email đã tồn tại
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    # Băm mật khẩu và tạo User
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()  # Phải commit để có new_user.id

    # ✅ Tạo UserInfo tương ứng
    user_info = UserInfo(
        user_id=new_user.id,
        full_name=username,
        email=email,
        gender='MALE',
        phone_number='',
        address='',
        job='',
        code=f'U{new_user.id:05d}',
        is_admin=False,
        vip=False,
        enabled=True,
        is_delete=False,
        start_date=datetime.datetime.utcnow(),
        last_online=datetime.datetime.utcnow(),
        use_number=0
    )

    db.session.add(user_info)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201




@user_bp.route('/patient-profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    profile_data = {
        'firstName': user.username,  # Hoặc user.first_name nếu bạn tách riêng
        'gender': user.gender or '',
        'email': user.email,
        'phone': user.phone or '',
        'address': user.address or '',
    }

    return jsonify(profile_data), 200

from app.models.user_info import UserInfo  # Đảm bảo bạn đã import đúng

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_patient_profile():
    user_info_id = request.args.get('userId', type=int)  # Thực chất là user_info.id

    if not user_info_id:
        return jsonify({'error': 'Missing userId'}), 400

    user_info = UserInfo.query.get(user_info_id)
    if not user_info:
        return jsonify({'error': 'UserInfo not found'}), 404

    user = user_info.user  # Quan hệ 1-1, từ user_info -> user
    if not user:
        return jsonify({'error': 'User not found'}), 404

    profile_data = {
        'firstName': user.username,
        'gender': user_info.gender or 'MALE',
        'email': user.email,
        'phone': user_info.phone_number or '',
        'address': user_info.address or '',
        'fullName': user_info.full_name or '',
        'job': user_info.job or '',
        'code': user_info.code or '',
        'vip': user_info.vip,
        'isAdmin': user_info.is_admin,
        'startDate': user_info.start_date.isoformat() if user_info.start_date else None,
        'lastOnline': user_info.last_online.isoformat() if user_info.last_online else None,
        'enabled': user_info.enabled
    }

    return jsonify(profile_data), 200

@user_bp.route('/patient-profile', methods=['PUT'])
@jwt_required()
def update_patient_profile():
    user_info_id = request.args.get('userId', type=int)  # Đây là user_info.id

    if not user_info_id:
        return jsonify({'error': 'Missing userId'}), 400

    user_info = UserInfo.query.get(user_info_id)  # ✅ Đúng rồi
    if not user_info:
        return jsonify({'error': 'UserInfo not found'}), 404

    data = request.get_json()

    user_info.job = data.get('job', user_info.job)
    user_info.full_name = data.get('fullName', user_info.full_name)
    user_info.phone_number = data.get('phone', user_info.phone_number)
    user_info.address = data.get('address', user_info.address)
    user_info.gender = data.get('gender', user_info.gender)

    db.session.commit()
    print("✅ Dữ liệu đã commit xong")

    return jsonify({'message': 'UserInfo updated successfully'}), 200

@user_bp.route('/user-info/all', methods=['GET'])
@jwt_required()
def get_all_user_info():
    user_info_list = UserInfo.query.filter_by(is_delete=False).all()

    result = []
    for info in user_info_list:
        result.append({
            "id": info.id,
            "userId": info.user_id,
            "username": info.user.username if info.user else None,
            "email": info.user.email if info.user else None,
            "fullName": info.full_name,
            "gender": info.gender,
            "job": info.job,
            "phoneNumber": info.phone_number,
            "address": info.address,
            "code": info.code,
            "isAdmin": info.is_admin,
            "vip": info.vip,
            "enabled": info.enabled,
            "startDate": info.start_date.isoformat() if info.start_date else None,
            "lastOnline": info.last_online.isoformat() if info.last_online else None,
            "useNumber": info.use_number
        })

    return jsonify(result), 200


@user_bp.route('/user-info', methods=['DELETE'])
@jwt_required()
def delete_user_info():
    user_info_id = request.args.get('userId', type=int)
    if not user_info_id:
        return jsonify({'error': 'Missing userId'}), 400

    user_info = UserInfo.query.get(user_info_id)
    if not user_info:
        return jsonify({'error': 'UserInfo not found'}), 404

    # Cập nhật cờ xóa mềm
    user_info.is_delete = True
    db.session.commit()

    return jsonify({'message': 'UserInfo marked as deleted (is_delete = true)'}), 200


@user_bp.route('/user-info/admin-status', methods=['PUT'])
@jwt_required()
def set_admin_status_bulk():
    data = request.get_json()

    user_ids = data.get('userIds')
    is_admin_value = data.get('value')

    if not user_ids or not isinstance(user_ids, list):
        return jsonify({'error': 'userIds must be a list of IDs'}), 400
    if is_admin_value is None:
        return jsonify({'error': 'Missing value in request body'}), 400

    updated = []
    skipped = []

    for user_info_id in user_ids:
        user_info = UserInfo.query.get(user_info_id)
        if user_info:
            user_info.is_admin = bool(is_admin_value)
            updated.append(user_info_id)
        else:
            skipped.append(user_info_id)

    db.session.commit()

    return jsonify({
        'message': f'Updated {len(updated)} user(s)',
        'updated': updated,
        'skipped': skipped
    }), 200
@user_bp.route('/set-vip', methods=['PUT'])
@jwt_required()
def set_user_vip():
    user_info_id = request.args.get('userId', type=int)

    if not user_info_id:
        return jsonify({'error': 'Missing userId'}), 400

    user_info = UserInfo.query.get(user_info_id)
    if not user_info:
        return jsonify({'error': 'UserInfo not found'}), 404

    if user_info.vip:
        return jsonify({'message': 'User is already VIP'}), 200

    user_info.vip = True
    db.session.commit()

    return jsonify({'message': 'User VIP status set to true'}), 200
