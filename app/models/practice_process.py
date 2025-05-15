# app/models/practice_process.py
from datetime import datetime
from ..extensions import db

class PracticeProcess(db.Model):
    __tablename__ = 'practice_process'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    practice_id = db.Column(db.Integer, db.ForeignKey('practice.id'), nullable=False)

    submit_code = db.Column(db.Text, nullable=True)  # Code người dùng đã nộp
    is_completed = db.Column(db.Boolean, default=False)  # Người dùng đã hoàn thành chưa
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='practice_processes')
    practice = db.relationship('Practice', back_populates='processes')
