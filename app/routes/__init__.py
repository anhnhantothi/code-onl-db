from .user_routes import user_bp
from .lesson_routes import lesson_bp
from .topic_lesson_routes import topic_lesson_bp
from app.routes.exercise_routes import exercise_bp
from app.routes.openai_routes import openai_bp


def register_routes(app):
    app.register_blueprint(user_bp)
    app.register_blueprint(lesson_bp)
    app.register_blueprint(topic_lesson_bp)
    app.register_blueprint(exercise_bp)

    app.register_blueprint(openai_bp, url_prefix='/api')