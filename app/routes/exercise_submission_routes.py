# app/routes/exercise_submission_routes.py
from flask import Blueprint, request, jsonify
from ..services.exercise_submission_service import submit_exercise, get_user_submissions

exercise_bp = Blueprint('exercise_submission', __name__)

@exercise_bp.route('/submit-exercise', methods=['POST'])
def submit():
    data = request.get_json()
    result = submit_exercise(data)
    return jsonify(result)


@exercise_bp.route('/user-submissions/<int:user_id>', methods=['GET'])
def user_submissions(user_id):
    submissions = get_user_submissions(user_id)
    return jsonify(submissions)