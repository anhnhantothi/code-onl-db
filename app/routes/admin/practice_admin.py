from flask import Blueprint, request, jsonify
from app.models.practice import Practice
from app.extensions import db
import json
import re
import unicodedata

admin_practice_bp = Blueprint('admin_practice', __name__)

# Hàm tạo slug
def slugify(text):
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)

@admin_practice_bp.route('/api/admin/add_practice', methods=['POST'])
def add_practice():
    data = request.json

    title = data.get('title')
    slug = slugify(title)
    difficulty = data.get('difficulty')  # 'EASY', 'MEDIUM', 'HARD'
    tags = data.get('tags', [])
    completion_rate = data.get('completionRate', 0.0)
    likes = data.get('likes', 0)
    description = data.get('description')

    # Check trùng slug
    if Practice.query.filter_by(slug=slug).first():
        return jsonify({"error": "Slug đã tồn tại. Hãy dùng tiêu đề khác."}), 400

    new_practice = Practice(
        title=title,
        slug=slug,
        difficulty=difficulty,
        tags=json.dumps(tags),
        completion_rate=completion_rate,
        likes=likes,
        description=description,
        active=True
    )
    db.session.add(new_practice)
    db.session.commit()

    return jsonify({
        "message": "✅ Thêm bài thành công!",
        "slug": new_practice.slug
    })
