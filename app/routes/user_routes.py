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

    access_token = create_access_token(identity=str(user.id))

    # Lấy thông tin từ user_info nếu có
    user_info = user.user_info
    info_dict = {
        'id': user.id,
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

    # Kiểm tra xem username hoặc email đã tồn tại chưa
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    # Hash password
    hashed_password = generate_password_hash(password)

    # Tạo user mới
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201



@user_bp.route('/patient-profile', methods=['GET'])
@jwt_required()
def get_patient_profile():
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

@user_bp.route('/patient-profile', methods=['PUT'])
@jwt_required()
def update_patient_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    # Cập nhật dữ liệu
    user.username = data.get('firstName', user.username)
    user.gender = data.get('gender', user.gender)
    user.email = data.get('email', user.email)
    user.phone = data.get('phone', user.phone)
    user.address = data.get('address', user.address)

    db.session.commit()

    return jsonify({'message': 'Profile updated successfully'}), 200