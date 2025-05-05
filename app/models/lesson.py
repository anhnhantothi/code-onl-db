from app.extensions import db

class Lesson(db.Model):
    __tablename__ = 'lesson'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    level = db.Column(db.String(50))
    description = db.Column(db.Text)
    topic_lesson_id = db.Column(db.Integer, db.ForeignKey('topic_lesson.id'), nullable=False)
    unlock_condition = db.Column(db.String(50), default='read')  # 'read' hoặc 'exercise'
    
    sublessons = db.relationship('Sublesson', backref='lesson', lazy=True)
    exercise = db.relationship('Exercise', uselist=False, backref='lesson')
