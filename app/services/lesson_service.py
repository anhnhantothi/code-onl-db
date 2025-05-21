# services/lesson_service.py
from app.models.topic_lesson import TopicLesson
from ..models.lesson import Lesson
from ..models.lesson_progress import LessonProgress
from flask_jwt_extended import get_jwt_identity

def get_lesson_with_sublessons(lesson_id, db_session):
    """
    Trả về dict lesson kèm danh sách sublessons và trạng thái completed
    Hoặc None nếu không tìm thấy lesson.
    """
    user_id = get_jwt_identity()
    # Lấy lesson
    lesson = db_session.query(Lesson).get(lesson_id)
    if not lesson:
        return None

    # Build sublessons
    sublessons = []
    for sl in lesson.sublessons:
        sublessons.append({
            'id': sl.id,
            'type': sl.type,
            'content': sl.content,
            'sort_order': sl.sort_order
        })

    # Kiểm tra progress
    progress = (
        db_session.query(LessonProgress)
        .filter_by(user_id=user_id, lesson_id=lesson_id)
        .first()
    )
    completed = progress.completed if progress else False

    return {
        'id': lesson.id,
        'title': lesson.title,
        'level': lesson.level,
        'description': lesson.description,
        'unlock_condition': lesson.unlock_condition,
        'completed': completed,
        # 'has_exercise': lesson.has_exercise,
        'sublessons': sorted(sublessons, key=lambda x: x['sort_order'])
    }


from ..models.exercise import Exercise  # ✅ import nếu chưa có

def _get_lesson_with_sublessons(lesson_id, db_session):
    # Lấy lesson
    lesson = db_session.query(Lesson).get(lesson_id)
    if not lesson:
        return None

    # Build sublessons
    sublessons = [
        {
            'id': sl.id,
            'type': sl.type,
            'content': sl.content,
            'sort_order': sl.sort_order
        }
        for sl in lesson.sublessons
    ]

    lesson_dict = {
        'id': lesson.id,
        'title': lesson.title,
        'level': lesson.level,
        'description': lesson.description,
        'unlock_condition': lesson.unlock_condition,
        'sublessons': sorted(sublessons, key=lambda x: x['sort_order'])
    }

    # ✅ Truy vấn Exercise nếu cần
    if lesson.unlock_condition == 'exercise':
        ex = db_session.query(Exercise).filter_by(lesson_id=lesson.id).first()
        if ex:
            lesson_dict['exercise'] = {
                'id': ex.id,
                'title': ex.title,
                'description': ex.description,
                'expected_output': ex.expected_output,
                'initial_code': ex.initial_code
            }

    return lesson_dict

def get_all_topics_full_data(db_session):
    topics = db_session.query(TopicLesson).order_by(TopicLesson.sort_order).all()
    result = []
    for topic in topics:
        # Lấy tất cả lesson thuộc topic
        lessons = db_session.query(Lesson).filter_by(topic_lesson_id=topic.id).order_by(Lesson.id).all()

        # Lấy lesson kèm sublessons bằng hàm chuyên dụng
        lesson_data = []
        for lesson in lessons:
            lesson_dict = _get_lesson_with_sublessons(lesson.id, db_session)
            if lesson_dict:
                lesson_data.append(lesson_dict)

        # Kết hợp vào topic
        topic_data = {
            'id': topic.id,
            'name': topic.name,
            'sort_order': topic.sort_order,
            'lessons': lesson_data
        }

        result.append(topic_data)

    return result