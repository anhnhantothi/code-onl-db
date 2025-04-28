from ..models.topic_lesson import TopicLesson

def get_all_topics_with_lessons():
    topics = TopicLesson.query.order_by(TopicLesson.sort_order).all()

    data = []
    for topic in topics:
        topic_data = {
            'id': topic.id,
            'name': topic.name,
            'lessons': [
                {
                    'id': lesson.id,
                    'title': lesson.title
                }
                for lesson in topic.lessons
            ]
        }
        data.append(topic_data)

    return data
