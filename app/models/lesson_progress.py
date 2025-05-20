from datetime import datetime
from ..extensions import db

class LessonProgress(db.Model):
    __tablename__ = 'lesson_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    submit_time = db.Column(db.DateTime,default=datetime.utcnow)
    # Relationships
    user = db.relationship('User', backref='lesson_progress')
    lesson = db.relationship('Lesson', backref='progress')
