from app import create_app
from app.extensions import db

from app.models.topic_lesson import TopicLesson
from app.models.lesson import Lesson
from app.models.sublesson import Sublesson
from app.models.exercise import Exercise
# from app.models.exercise_submission import ExerciseSubmission
from app.models.user import User
from app.models.lesson_progress import LessonProgress
from app.models.certificate import Certificate
from app.models.practice_process import PracticeProcess
from app.models.practice import Practice
from app.models.user_info import UserInfo



app = create_app()

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
