# app/models/comment.py
from ..extensions import db
from datetime import datetime

class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    practice_id = db.Column(db.Integer, db.ForeignKey('practice.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)

    user = db.relationship('User', backref='comments')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='joined')
