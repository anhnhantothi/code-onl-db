# app/routes/lesson_progress_routes.py
from flask import Blueprint, request, jsonify
from ..services.lesson_progress_service import update_progress, get_progress_by_user

progress_bp = Blueprint('lesson_progress', __name__)

@progress_bp.route('/update-progress', methods=['POST'])
def update():
    data = request.get_json()
    updated = update_progress(data)
    return jsonify(updated)


@progress_bp.route('/progress/<int:user_id>', methods=['GET'])
def get_progress(user_id):
    progress = get_progress_by_user(user_id)
    return jsonify(progress)