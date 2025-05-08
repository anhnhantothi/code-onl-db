# app/services/exercise_service.py

from flask_jwt_extended import get_jwt_identity
from app.models.exercise_submission import ExerciseSubmission
from app.models.lesson import Lesson
from app.models.lesson_progress import LessonProgress
from app.models.exercise import Exercise
from app.extensions import db


def get_exercise_by_id(exercise_id):
    return Exercise.query.get(exercise_id)


def get_exercise_by_lesson_id(lesson_id):
    return Exercise.query.filter_by(lesson_id=lesson_id).first()


def create_exercise_for_lesson(data, lesson_id):
    # Tạo bài tập mới
    exercise = Exercise(
        lesson_id=lesson_id,
        title=data['title'],
        description=data['description'],
        initial_code=data['initial_code'],
        expected_output=data['expected_output']
    )
    db.session.add(exercise)

    # Cập nhật lesson.unlock_condition
    lesson = Lesson.query.get(lesson_id)
    if lesson:
        lesson.unlock_condition = 'exercise'

    db.session.commit()
    return exercise


def delete_exercise_and_update_lesson(exercise_id):
    exercise = Exercise.query.get(exercise_id)
    if not exercise:
        return False, "Exercise not found"

    lesson = Lesson.query.get(exercise.lesson_id)
    db.session.delete(exercise)

    if lesson:
        lesson.unlock_condition = 'read'

    db.session.commit()
    return True, "Exercise deleted and lesson updated"


def save_submission(exercise_id, submitted_code, actual_output, is_correct):
    user_id = get_jwt_identity()

    # Lưu bài nộp
    submission = ExerciseSubmission(
        user_id=user_id,
        exercise_id=exercise_id,
        submitted_code=submitted_code,
        actual_output=actual_output,
        is_correct=is_correct
    )
    db.session.add(submission)

    # Nếu đúng thì cập nhật lesson_progress.completed = True
    if is_correct:
        exercise = Exercise.query.get(exercise_id)
        if exercise:
            lesson_id = exercise.lesson_id
            progress = LessonProgress.query.filter_by(
                user_id=user_id,
                lesson_id=lesson_id
            ).first()
            if not progress:
                progress = LessonProgress(
                    user_id=user_id,
                    lesson_id=lesson_id,
                    completed=True
                )
                db.session.add(progress)
            else:
                progress.completed = True

    db.session.commit()
