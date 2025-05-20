# app/services/comment_service.py
from app.models.comment import Comment
from app.extensions import db

def get_comments_by_practice(practice_id):
    all_comments = Comment.query.filter_by(practice_id=practice_id).order_by(Comment.created_at.desc()).all()
    lv0 = [c for c in all_comments if c.parent_id is None]
    lv1 = [c for c in all_comments if c.parent_id is not None]

    def get_replies(parent_id):
        return [reply for reply in lv1 if reply.parent_id == parent_id]

    result = []
    for comment in lv0:
        dto = comment_to_dict(comment)
        dto['replies'] = [comment_to_dict(r) for r in get_replies(comment.id)]
        result.append(dto)

    return result

def add_comment(data):
    comment = Comment(
        content=data['content'],
        user_id=data['user_id'],
        practice_id=data['practice_id'],
        parent_id=data.get('parent_id')
    )
    db.session.add(comment)
    db.session.commit()
    return comment_to_dict(comment)

def like_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if comment:
        comment.likes += 1
        db.session.commit()
    return comment_to_dict(comment)

def comment_to_dict(comment):
    return {
        "id": comment.id,
        "user_id": comment.user_id,
        "practice_id": comment.practice_id,
        "content": comment.content,
        "likes": comment.likes,
        "created_at": comment.created_at.isoformat(),
        "username": comment.user.username,  # <- Lấy từ quan hệ
        "replies": [comment_to_dict(reply) for reply in getattr(comment, 'replies', [])]
    }