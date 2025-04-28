from ..extensions import db

class Sublesson(db.Model):
    __tablename__ = 'sublesson'

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    type = db.Column(db.Enum('title', 'text', 'cmd', 'example'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sort_order = db.Column(db.Integer, default=0)
