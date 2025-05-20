# app/routes/comment_routes.py
from flask import Blueprint, request, jsonify
from app.services import comment_service

comment_bp = Blueprint('comment', __name__, url_prefix='/api/comments')

@comment_bp.route('/', methods=['GET'])
def get_comments():
    practice_id = request.args.get('practice_id')
    # print(practice_id,"nhàn")
    if not practice_id:
        return jsonify({'error': 'Missing practice_id'}), 400
    return jsonify(comment_service.get_comments_by_practice(int(practice_id)))

@comment_bp.route('', methods=['POST'])
def create_comment():
    data = request.json
    return jsonify(comment_service.add_comment(data)), 201

@comment_bp.route('/like/<int:comment_id>', methods=['POST'])
def like(comment_id):
    return jsonify(comment_service.like_comment(comment_id))
