# app/models/practice.py
from ..extensions import db

class Practice(db.Model):
    __tablename__ = 'practice'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    difficulty = db.Column(db.Enum('EASY', 'MEDIUM', 'HARD', name='difficulty_enum'), nullable=False)
    tags = db.Column(db.Text, nullable=True)   # Lưu dưới dạng JSON string hoặc comma-separated string
    completion_rate = db.Column(db.Float, default=0.0)
    likes = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text, nullable=False)   # Đề bài
    slug = db.Column(db.String(255), unique=True)
    is_delete = db.Column(db.Boolean, default=False)

    # Relationship
    processes = db.relationship('PracticeProcess', back_populates='practice')
