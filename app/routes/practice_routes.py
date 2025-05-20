from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import jwt_required
from slugify import slugify
from app.models.practice import Practice
from app.extensions import db
import json

practice_bp = Blueprint('practice', __name__)

@practice_bp.route('/api/practices', methods=['GET'])
def get_practices():
    active_param = request.args.get('active')  # dạng chuỗi: 'true', 'false', hoặc None

    query = Practice.query.filter_by(is_delete=False)

    # Nếu có truyền active thì lọc
    if active_param is not None:
        if active_param.lower() == 'true':
            query = query.filter_by(active=True)
        elif active_param.lower() == 'false':
            query = query.filter_by(active=False)
        else:
            return jsonify({'error': 'Invalid active value, must be true or false'}), 400

    practices = query.order_by(Practice.id.desc()).all()

    result = []
    for p in practices:
        result.append({
            "title": p.title,
            "slug": p.slug,
            "difficulty": p.difficulty,
            "tags": json.loads(p.tags) if p.tags else [],
            "completionRate": p.completion_rate,
            "likes": p.likes,
            "isActive": p.active,
            "id": p.id
        })

    return jsonify(result), 200

@practice_bp.route('/api/practices/slug/<string:slug>', methods=['GET'])
def get_practice_by_slug(slug):
    practice = Practice.query.filter_by(slug=slug).first()

    if not practice:
        abort(404, description="Practice not found")

    return jsonify({
        'id': practice.id,
        'title': practice.title,
        'slug': practice.slug,
        'difficulty': practice.difficulty,
        'tags': json.loads(practice.tags) if practice.tags else [],
        'completionRate': practice.completion_rate,
        'likes': practice.likes,
        'description': practice.description,
        'slug': practice.slug
    })

@practice_bp.route('/api/practices/delete', methods=['PUT'])
@jwt_required()
def soft_delete_practice():
    practice_id = request.args.get('practiceId', type=int)
    if not practice_id:
        return jsonify({'error': 'Missing practiceId'}), 400

    practice = Practice.query.get(practice_id)
    if not practice:
        return jsonify({'error': 'Practice not found'}), 404

    practice.is_delete = True
    db.session.commit()

    return jsonify({
        'message': f'Practice {practice_id} marked as deleted (is_delete = true)',
        'isDelete': True
    }), 200
@practice_bp.route('/api/practices/active-status', methods=['PUT'])
@jwt_required()
def update_practice_active_status():
    practice_id = request.args.get('practiceId', type=int)
    if not practice_id:
        return jsonify({'error': 'Missing practiceId'}), 400

    data = request.get_json()
    if 'value' not in data:
        return jsonify({'error': 'Missing value in request body'}), 400

    practice = Practice.query.get(practice_id)
    if not practice:
        return jsonify({'error': 'Practice not found'}), 404

    practice.active = bool(data['value'])
    db.session.commit()

    return jsonify({
        'message': f'Practice active status set to {practice.active}',
        'isActive': practice.active
    }), 200

@practice_bp.route('/api/practices/update', methods=['PUT'])
@jwt_required()
def update_practice():
    practice_id = request.args.get('practiceId', type=int)
    if not practice_id:
        return jsonify({'error': 'Missing practiceId'}), 400

    practice = Practice.query.get(practice_id)
    if not practice:
        return jsonify({'error': 'Practice not found'}), 404

    data = request.get_json()

    # Cập nhật các trường nếu có trong body
    if 'title' in data:
        practice.title = data['title']
    if 'difficulty' in data:
        practice.difficulty = data['difficulty']
    if 'tags' in data:
        practice.tags = json.dumps(data['tags'])  # Lưu tags dạng chuỗi JSON
    if 'description' in data:
        practice.description = data['description']

    db.session.commit()

    return jsonify({'message': 'Practice updated successfully'}), 200

@practice_bp.route('/api/practices/create', methods=['POST'])
@jwt_required()
def create_practice():
    data = request.get_json()

    title = data.get('title')
    difficulty = data.get('difficulty')
    tags = data.get('tags', [])
    description = data.get('description', '')
    active = data.get('active', True)

    if not title or not difficulty:
        return jsonify({'error': 'Missing title or difficulty'}), 400

    # Tạo slug tự động (nếu bạn có hàm xử lý)
    slug = slugify(title)

    new_practice = Practice(
        title=title,
        slug=slug,
        difficulty=difficulty,
        tags=json.dumps(tags),
        description=description,
        active=active,
        is_delete=False,
        completion_rate=0.0,
        likes=0
    )

    db.session.add(new_practice)
    db.session.commit()

    return jsonify({'message': 'Practice created successfully', 'id': new_practice.id}), 201
