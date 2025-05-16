from .user_routes import user_bp
from .lesson_routes import lesson_bp
from .topic_lesson_routes import topic_lesson_bp
from .exercise_routes import exercise_bp
from .openai_routes import openai_bp
from .certificate_routes import cert_bp
from .code_runner_routes import code_runner_bp
from .practice_routes import practice_bp
from .admin.practice_admin import admin_practice_bp

def register_routes(app):
    app.register_blueprint(user_bp)
    app.register_blueprint(lesson_bp)
    app.register_blueprint(topic_lesson_bp)
    app.register_blueprint(exercise_bp)

    app.register_blueprint(openai_bp, url_prefix='/api')

    app.register_blueprint(cert_bp)

    app.register_blueprint(code_runner_bp, url_prefix='/api')
    app.register_blueprint(practice_bp)

    # ----------- Admin-----------
    app.register_blueprint(admin_practice_bp)