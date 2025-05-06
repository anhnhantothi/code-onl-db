from ..models.exercise_submission import ExerciseSubmission
from ..models.exercise import Exercise
from ..extensions import db

def submit_exercise(data):
    submission = ExerciseSubmission(
        user_id=data['user_id'],
        exercise_id=data['exercise_id'],
        submitted_code=data['submitted_code'],
        actual_output=data['actual_output'],
        is_correct=data['is_correct']
    )
    db.session.add(submission)
    db.session.commit()
    return {'message': 'Submission saved successfully'}

def get_user_submissions(user_id):
    submissions = ExerciseSubmission.query.filter_by(user_id=user_id).all()
    return [
        {
            'exercise_id': s.exercise_id,
            'submitted_code': s.submitted_code,
            'actual_output': s.actual_output,
            'is_correct': s.is_correct
        } for s in submissions
    ]
