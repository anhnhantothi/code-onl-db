from ..extensions import db

class ExerciseSubmission(db.Model):
    __tablename__ = 'exercise_submission'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    submitted_code = db.Column(db.Text, nullable=False)
    actual_output = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)

    # Relationships
    user = db.relationship('User', backref='submissions')
    exercise = db.relationship('Exercise', backref='submissions')
