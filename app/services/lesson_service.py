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
        'sublessons': sorted(sublessons, key=lambda x: x['sort_order'])
    }
