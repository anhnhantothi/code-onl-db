# app/services/lesson_progress_service.py
from app.models.lesson import Lesson
from ..models.lesson_progress import LessonProgress
from ..extensions import db

def update_progress(data):
    progress = LessonProgress.query.filter_by(user_id=data['user_id'], lesson_id=data['lesson_id']).first()
    if progress:
        progress.completed = data['completed']
    else:
        progress = LessonProgress(
            user_id=data['user_id'],
            lesson_id=data['lesson_id'],
            completed=data['completed']
        )
        db.session.add(progress)
    db.session.commit()
    return {'message': 'Progress updated'}

def get_progress_by_user(user_id):
    progresses = LessonProgress.query.filter_by(user_id=user_id).all()
    return [
        {
            'lesson_id': p.lesson_id,
            'completed': p.completed
        } for p in progresses
    ]

def get_topic_progress(user_id: int, topic_id: int) -> dict:
    """
    Trả về dict: {
      'topicId': topic_id,
      'userId': user_id,
      'completed': completed_count,
      'total': total_lessons,
      'percent': percent
    }
    """
    # Tổng số lesson trong topic
    total_lessons = Lesson.query.filter_by(topic_id=topic_id).count()

    # Số lesson đã hoàn thành
    completed_count = (
        db.session.query(LessonProgress)
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .filter(
            LessonProgress.user_id   == user_id,
            Lesson.topic_id          == topic_id,
            LessonProgress.completed == True
        )
        .count()
    )

    percent = round((completed_count / total_lessons * 100), 2) if total_lessons else 0

    return {
        'topicId':   topic_id,
        'userId':    user_id,
        'completed': completed_count,
        'total':     total_lessons,
        'percent':   percent
    }