# app/routes/exercise_routes.py

import re
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extensions import db
from app.models.exercise import Exercise
from app.services.exercise_service import (
    get_exercise_by_id,
    get_exercise_by_lesson_id,
    create_exercise_for_lesson,
    delete_exercise_and_update_lesson,
    save_submission
)
from app.utils.code_runner import run_python_code

exercise_bp = Blueprint('exercise', __name__)

def normalize(s: str) -> str:
    """
    1. Loại bỏ BOM và CR (\r)
    2. Gom mọi whitespace (space, tab, newline) thành 1 space
    3. Strip đầu-cuối
    """
    s = s.lstrip('\ufeff').replace('\r', '')
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

@exercise_bp.route('/lesson/<int:lesson_id>/exercise', methods=['GET'])
def route_get_exercise_by_lesson(lesson_id):
    """Lấy bài tập theo lesson_id"""
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
    }), 200


@exercise_bp.route('/exercise/<int:exercise_id>', methods=['GET'])
def route_get_exercise(exercise_id):
    """Lấy thông tin 1 bài tập theo ID"""
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
    }), 200


@exercise_bp.route('/exercise/<int:lesson_id>', methods=['POST'])
@jwt_required()
def route_create_exercise(lesson_id):
    """Tạo mới exercise cho lesson và set unlock_condition"""
    data = request.get_json() or {}
    required = ('title', 'description', 'initial_code', 'expected_output')
    if any(field not in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400

    exercise = create_exercise_for_lesson(data, lesson_id)
    return jsonify({
        'message': 'Exercise created.',
        'exercise_id': exercise.id
    }), 201


@exercise_bp.route('/exercise/<int:exercise_id>', methods=['DELETE'])
@jwt_required()
def route_delete_exercise(exercise_id):
    """Xóa exercise và reset unlock_condition của lesson"""
    success, msg = delete_exercise_and_update_lesson(exercise_id)
    if not success:
        return jsonify({'error': msg}), 404

    return jsonify({'message': msg}), 200


@exercise_bp.route('/exercise/<int:exercise_id>/submit', methods=['POST'])
@jwt_required()
def route_submit_exercise(exercise_id):
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    code = data.get('code','').strip()
    if not code:
        return jsonify({'error': 'Chưa gửi mã nguồn'}), 400

    exercise = Exercise.query.get(exercise_id)
    if not exercise:
        return jsonify({'error': 'Không tìm thấy bài tập'}), 404

    # 1. Chạy code
    try:
        actual_output = run_python_code(code)
    except Exception as e:
        return jsonify({'error': f'Lỗi khi chạy code: {e}'}), 500

    # 2. Chuẩn hoá
    exp_raw = exercise.expected_output or ''
    expected_norm = normalize(exp_raw)
    actual_norm   = normalize(actual_output)

    # 3. So sánh
    # 3.1 case-insensitive nếu không yêu cầu case-sensitive
    if not getattr(exercise, 'case_sensitive', False):
        expected_norm = expected_norm.lower()
        actual_norm   = actual_norm.lower()

    # 3.2 thử số học nếu cả hai parse được float
    is_correct = False
    try:
        exp_num = float(expected_norm)
        act_num = float(actual_norm)
        # cho phép sai số nhỏ
        is_correct = abs(exp_num - act_num) < 1e-6
    except ValueError:
        # 3.3 hỗ trợ nhiều đáp án cách nhau bởi '|'
        # ví dụ expected_output = "Yes|Y|True"
        variants = [normalize(v) for v in exp_raw.split('|')]
        if not getattr(exercise, 'case_sensitive', False):
            variants = [v.lower() for v in variants]
        is_correct = any(actual_norm == variant for variant in variants)

    # 4. Lưu submission và (nếu đúng) auto-update lesson_progress
    try:
        save_submission(
            exercise_id=exercise_id,
            submitted_code=code,
            actual_output=actual_output,
            is_correct=is_correct
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Lỗi khi lưu submission: {e}'}), 500

    # 5. Phản hồi cho frontend
    return jsonify({
        'correct': is_correct,
        'actual_output': actual_output
    }), 200