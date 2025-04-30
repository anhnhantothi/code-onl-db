from ..extensions import db

class Exercise(db.Model):
    __tablename__ = 'exercise'

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    initial_code = db.Column(db.Text, nullable=False)  # Code ban đầu user sẽ thấy
    expected_output = db.Column(db.Text, nullable=False)  # Kết quả mong đợi
