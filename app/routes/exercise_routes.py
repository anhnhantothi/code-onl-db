from flask import Blueprint, jsonify
from ..services.exercise_service import get_exercise_by_id, get_exercise_by_lesson_id

exercise_bp = Blueprint('exercise', __name__)

@exercise_bp.route('/exercise/<int:exercise_id>', methods=['GET'])
def get_exercise(exercise_id):
    exercise = get_exercise_by_id(exercise_id)
    if not exercise:
        return jsonify({'error': 'Exercise not found'}), 404

    return jsonify({
        'id': exercise.id,
        'lesson_id': exercise.lesson_id,
        'title': exercise.title,
        'description': exercise.description,
        'initial_code': exercise.initial_code,
        'expected_output': exercise.expected_output
    })

@exercise_bp.route('/lesson/<int:lesson_id>/exercise', methods=['GET'])
def get_exercise_by_lesson(lesson_id):
    exercise = get_exercise_by_lesson_id(lesson_id)
    if not exercise:
        return jsonify({'error': 'Exercise not found for this lesson'}), 404

    return jsonify({
        'id': exercise.id,
        'lesson_id': exercise.lesson_id,
        'title': exercise.title,
        'description': exercise.description,
        'initial_code': exercise.initial_code,
        'expected_output': exercise.expected_output
    })
