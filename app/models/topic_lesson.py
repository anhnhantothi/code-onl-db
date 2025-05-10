# app/models/topic_lesson.py
from ..extensions import db

class TopicLesson(db.Model):
    __tablename__ = 'topic_lesson'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.Integer, default=0)

    lessons      = db.relationship('Lesson',    backref='topic_lesson', lazy=True)
    certificate = db.relationship('Certificate', back_populates='topic')
