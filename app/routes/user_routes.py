from flask import Blueprint, request, jsonify
from ..models.user import User
from ..extensions import db
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

user_bp = Blueprint('user', __name__)

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'error': 'Invalid username or password'}), 400

    if not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid username or password'}), 400

    return jsonify({'message': 'Login successful'}), 200

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