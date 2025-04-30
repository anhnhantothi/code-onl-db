from app import create_app
from app.extensions import db

from app.models.topic_lesson import TopicLesson
from app.models.lesson import Lesson
from app.models.sublesson import Sublesson

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
