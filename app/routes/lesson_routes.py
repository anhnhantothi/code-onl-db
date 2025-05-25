from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.lesson import Lesson
from app.models.lesson_progress import LessonProgress
from ..services.lesson_service import get_lesson_with_sublessons
from ..extensions import db


lesson_bp = Blueprint('lesson', __name__)

@lesson_bp.route('/lesson/<int:lesson_id>', methods=['GET'])
@jwt_required()
def get_lesson(lesson_id):
    # Gọi service, truyền luôn db.session
    lesson_data = get_lesson_with_sublessons(lesson_id, db.session)
    if lesson_data:
        return jsonify(lesson_data), 200

    return jsonify({'error': 'Lesson not found'}), 404


@lesson_bp.route('/lesson/<int:lesson_id>/complete', methods=['POST'])
@jwt_required()
def mark_lesson_complete(lesson_id):
    user_id = get_jwt_identity()

    # Kiểm tra nếu đã có thì bỏ qua
    existing = LessonProgress.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
    if existing:
        return jsonify({'message': 'Already completed'}), 200

    # Tạo bản ghi hoàn thành mới
    progress = LessonProgress(user_id=user_id, lesson_id=lesson_id, completed=True)
    db.session.add(progress)
    db.session.commit()

    return jsonify({'message': 'Lesson marked as completed'}), 200

@lesson_bp.route('/topics/<int:topic_id>/lessons', methods=['GET'])
@jwt_required()
def get_lessons_by_topic(topic_id):
    lessons = Lesson.query.filter_by(topic_lesson_id=topic_id).all()
    result = []
    for lesson in lessons:
        result.append({
            "id": lesson.id,
            "title": lesson.title,
            "level": lesson.level,
            "description": lesson.description,
            "has_exercise": lesson.has_exercise,
        })
    return jsonify(result), 200