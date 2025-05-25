# app/routes/lesson_progress_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models.lesson_progress import LessonProgress
from ..services.lesson_progress_service import get_topic_progress, update_progress, get_progress_by_user

progress_bp = Blueprint('lesson_progress', __name__)

# @progress_bp.route('/update-progress', methods=['POST'])
# def update():
#     data = request.get_json()
#     updated = update_progress(data)
#     return jsonify(updated)


# @progress_bp.route('/progress/<int:user_id>', methods=['GET'])
# def get_progress(user_id):
#     progress = get_progress_by_user(user_id)
#     return jsonify(progress)

# @progress_bp.route('/topic/<int:topic_id>', methods=['GET'])
# def topic_progress(topic_id):
#     """
#     GET /api/lesson-progress/topic/<topic_id>?userId=<user_id>
#     """
#     user_id = request.args.get('userId', type=int)
#     if not user_id:
#         return jsonify({'error': 'Missing parameter userId'}), 400

#     result = get_topic_progress(user_id, topic_id)
#     return jsonify(result), 200

@progress_bp.route('/lesson/<int:lesson_id>/status', methods=['GET'])
@jwt_required()
def get_lesson_status(lesson_id):
    user_id = get_jwt_identity()
    progress = LessonProgress.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
    return jsonify({
        "completed": bool(progress),
        "submitted_at": progress.submit_time.isoformat() if progress else None
        })
