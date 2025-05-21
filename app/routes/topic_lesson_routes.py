from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.extensions import db

from app.models.exercise import Exercise
from app.models.lesson import Lesson
from app.models.sublesson import Sublesson
from app.models.topic_lesson import TopicLesson
from app.services.lesson_service import get_all_topics_full_data

topic_lesson_bp = Blueprint('topic_lesson', __name__)

@topic_lesson_bp.route('/topics', methods=['GET'])
def get_topics():
    # user_id = get_jwt_identity()
    data = get_all_topics_full_data(db.session)
    return jsonify(data), 200

@topic_lesson_bp.route('/api/topic', methods=['POST'])
@jwt_required()
def create_topic_with_all_data():
    data = request.get_json()

    try:
        # 1. Tạo Topic
        topic = TopicLesson(
            name=data['name'],
            sort_order=data.get('sort_order', 0)
        )
        db.session.add(topic)
        db.session.flush()  # để có topic.id

        # 2. Thêm Lessons
        for l in data.get('lessons', []):
            lesson = Lesson(
                title=l['title'],
                level=l['level'],
                description=l['description'],
            
                unlock_condition=l.get('unlock_condition', 'read'),
                topic_lesson_id=topic.id
            )
            db.session.add(lesson)
            db.session.flush()

            # 3. Thêm Sublessons
            for sl in l.get('sublessons', []):
                sub = Sublesson(
                    lesson_id=lesson.id,
                    type=sl['type'],
                    content=sl['content'],
                    sort_order=sl['sort_order']
                )
                db.session.add(sub)

            # 4. Nếu là bài tập thì thêm Exercise
            if lesson.unlock_condition == 'exercise' and 'exercise' in l:
                ex = l['exercise']
                exercise = Exercise(
                    lesson_id=lesson.id,
                    title=ex.get('title'),
                    description=ex.get('description'),
                    initial_code=ex.get('initial_code') or '',
                    expected_output=ex.get('expected_output', '')
                )
                db.session.add(exercise)

        db.session.commit()
        return jsonify({'message': 'Tạo topic và các bài học thành công'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
@topic_lesson_bp.route('/api/topic/<int:topic_id>', methods=['PUT'])
@jwt_required()
def update_topic(topic_id):
    data = request.get_json()
    try:
        topic = db.session.get(TopicLesson, topic_id)
        if not topic:
            return jsonify({'error': 'Topic not found'}), 404

        # Cập nhật thông tin topic
        topic.name = data.get('name', topic.name)
        topic.sort_order = data.get('sort_order', topic.sort_order)

        # Duyệt qua lesson cũ để xoá những lesson không còn
        current_lessons = {l.id for l in topic.lessons}
        incoming_lessons = {l['id'] for l in data.get('lessons', []) if l.get('id')}
        for lesson_id in current_lessons - incoming_lessons:
            Lesson.query.filter_by(id=lesson_id).delete()

        # Thêm hoặc cập nhật lesson
        for l in data.get('lessons', []):
            if l.get('id'):
                lesson = Lesson.query.get(l['id'])
            else:
                lesson = Lesson(topic_lesson_id=topic.id)
                db.session.add(lesson)

            lesson.title = l['title']
            lesson.level = l['level']
            lesson.description = l['description']
            lesson.unlock_condition = l.get('unlock_condition', 'read')
            db.session.flush()

            # Xử lý sublessons
            current_subs = {s.id for s in lesson.sublessons}
            incoming_subs = {s['id'] for s in l.get('sublessons', []) if s.get('id')}
            for sid in current_subs - incoming_subs:
                Sublesson.query.filter_by(id=sid).delete()

            for sl in l.get('sublessons', []):
                if sl.get('id'):
                    sub = Sublesson.query.get(sl['id'])
                else:
                    sub = Sublesson(lesson_id=lesson.id)
                    db.session.add(sub)
                sub.type = sl['type']
                sub.content = sl['content']
                sub.sort_order = sl['sort_order']

            # Xử lý exercise
            if lesson.unlock_condition == 'exercise':
                ex_data = l.get('exercise', {})
                exercise = Exercise.query.filter_by(lesson_id=lesson.id).first()
                if not exercise:
                    exercise = Exercise(lesson_id=lesson.id)
                    db.session.add(exercise)

                exercise.title = ex_data.get('title', '')
                exercise.description = ex_data.get('description', '')
                exercise.initial_code = ex_data.get('initial_code', '')
                exercise.expected_output = ex_data.get('expected_output', '')
            else:
                Exercise.query.filter_by(lesson_id=lesson.id).delete()

        db.session.commit()
        return jsonify({'message': 'Cập nhật topic thành công'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400