from flask import Flask,jsonify
import os
from .config import DevelopmentConfig,ProductionConfig
from .database import init_db
from .routes import register_blueprints
def create_app():
    app=Flask(__name__)
    if os.getenv('FLASK_ENV') == 'development':
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(ProductionConfig)
    init_db(app)
    register_blueprints(app)
    @app.route('/')
    def home():
        return jsonify({'message':"welcome to domain speific llm"})
    return app