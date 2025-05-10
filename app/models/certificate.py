# app/models/certificate.py
from datetime import datetime
from ..extensions import db

class Certificate(db.Model):
    __tablename__ = 'certificate'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'),   nullable=False)
    topic_id   = db.Column(db.Integer, db.ForeignKey('topic_lesson.id'), nullable=False)
    issued_at  = db.Column(db.DateTime, default=datetime.utcnow,     nullable=False)
    pdf_path   = db.Column(db.String(255), nullable=False)

    # Quan hệ 2 chiều
    user  = db.relationship('User',         back_populates='certificate')
    topic = db.relationship('TopicLesson',  back_populates='certificate')
