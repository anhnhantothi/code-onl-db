from flask import Blueprint, jsonify
from ..services.lesson_service import get_lesson_with_sublessons

lesson_bp = Blueprint('lesson', __name__)

@lesson_bp.route('/lesson/<int:lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    lesson = get_lesson_with_sublessons(lesson_id)
    if lesson:
        return jsonify(lesson), 200
    return jsonify({'error': 'Lesson not found'}), 404
