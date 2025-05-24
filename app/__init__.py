from flask import Flask
from flask_jwt_extended import JWTManager
from .config import Config
from .extensions import db
from .routes import register_routes
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    jwt = JWTManager(app)

    db.init_app(app)
    from app import models

    # Enable CORS
    # CORS(app)
    CORS(app, supports_credentials=True, resources={
        r"/*": {"origins": "http://localhost:5173"}
    })
    register_routes(app)

    return app
