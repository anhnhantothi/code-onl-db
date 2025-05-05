from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import jwt_required
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

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token
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