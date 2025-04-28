from ..models.lesson import Lesson

def get_lesson_with_sublessons(lesson_id):
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return None

    sublessons = [
        {
            'id': sub.id,
            'type': sub.type,
            'content': sub.content,
            'sort_order': sub.sort_order
        }
        for sub in sorted(lesson.sublessons, key=lambda s: s.sort_order)
    ]

    lesson_data = {
        'id': lesson.id,
        'title': lesson.title,
        'level': lesson.level,
        'description': lesson.description,
        'sublessons': sublessons
    }

    return lesson_data
