# file: app/routes/useAIchat_routes.py
from flask import Blueprint, jsonify
from app.models.user_info import UserInfo
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extensions import db

chat_bp = Blueprint('chat', __name__)

MAX_FREE_USES = 4


@chat_bp.route('/use-chat', methods=['POST'])
@jwt_required()
def use_chat():
    user_id = get_jwt_identity()
    user_info = UserInfo.query.filter_by(user_id=user_id).first()

    if not user_info:
        return jsonify({'error': 'User info not found'}), 404

    if not user_info.vip and user_info.use_number >= MAX_FREE_USES:
        return jsonify({
            'error': 'Bạn đã dùng hết lượt miễn phí.',
            'require_vip': True,
            'current_use': user_info.use_number
        }), 403

    # Tăng lượt sử dụng
    user_info.use_number += 1
    db.session.commit()

    return jsonify({
        'message': 'Success',
        'current_use': user_info.use_number,
        'require_vip': False
    })

@chat_bp.route('/check-chat-limit', methods=['GET'])
@jwt_required()
def check_chat_limit():
    user_id = get_jwt_identity()
    print(user_id)
    user_info = UserInfo.query.filter_by(user_id=user_id).first()

    if not user_info:
        return jsonify({'error': 'User info not found'}), 404

    allow = user_info.vip or user_info.use_number < MAX_FREE_USES

    return jsonify({
        'allow': allow,
        'vip': user_info.vip,
        'current_use': user_info.use_number,
        'require_vip': not allow
    })