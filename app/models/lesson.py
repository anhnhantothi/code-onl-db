from ..extensions import db

class Lesson(db.Model):
    __tablename__ = 'lesson'

    id = db.Column(db.Integer, primary_key=True)
    topic_lesson_id = db.Column(db.Integer, db.ForeignKey('topic_lesson.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    level = db.Column(db.String(50))
    description = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)

    sublessons = db.relationship('Sublesson', backref='lesson', lazy=True)
