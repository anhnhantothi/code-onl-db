from flask_cors import CORS
from .user_routes import user_bp
from .lesson_routes import lesson_bp
from .topic_lesson_routes import topic_lesson_bp
from .exercise_routes import exercise_bp
from .openai_routes import openai_bp
from .certificate_routes import cert_bp
from .code_runner_routes import code_runner_bp
from .practice_routes import practice_bp
from .admin.practice_admin import admin_practice_bp
from .comment_routes import comment_bp
from .analytics_routes import analytics_bp
from .lesson_progress_routes import progress_bp
from .useAIchat_routes import chat_bp

def register_routes(app):
    app.register_blueprint(user_bp)
    app.register_blueprint(lesson_bp)
    app.register_blueprint(topic_lesson_bp)
    app.register_blueprint(exercise_bp)

    app.register_blueprint(openai_bp, url_prefix='/api')

    app.register_blueprint(cert_bp)

    app.register_blueprint(code_runner_bp, url_prefix='/api')
    app.register_blueprint(practice_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(progress_bp, url_prefix='/api/lesson-progress')

    app.register_blueprint(chat_bp, url_prefix='/api')
    # ----------- Admin-----------
    app.register_blueprint(admin_practice_bp)
    app.register_blueprint(analytics_bp)
