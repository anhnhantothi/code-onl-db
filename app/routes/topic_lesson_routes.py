from flask import Blueprint, jsonify
from ..services.topic_lesson_service import get_all_topics_with_lessons

topic_lesson_bp = Blueprint('topic_lesson', __name__)

@topic_lesson_bp.route('/topics', methods=['GET'])
def get_topics():
    data = get_all_topics_with_lessons()
    return jsonify(data), 200
