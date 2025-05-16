from flask import Blueprint, abort, jsonify
from app.models.practice import Practice
import json

practice_bp = Blueprint('practice', __name__)

@practice_bp.route('/api/practices', methods=['GET'])
def get_practices():
    practices = Practice.query.filter_by(active=True).all()
    result = []
    for p in practices:
        result.append({
            "title": p.title,
            "slug": p.slug,
            "difficulty": p.difficulty,  # 'EASY', 'MEDIUM', 'HARD'
            "tags": json.loads(p.tags) if p.tags else [],
            "completionRate": p.completion_rate,
            "likes": p.likes,
        })
    return jsonify(result)

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

