from ..models.exercise import Exercise

def get_exercise_by_id(exercise_id):
    return Exercise.query.get(exercise_id)

def get_exercise_by_lesson_id(lesson_id):
    return Exercise.query.filter_by(lesson_id=lesson_id).first()
