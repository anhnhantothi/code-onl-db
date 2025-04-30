# app/services/lesson_progress_service.py
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