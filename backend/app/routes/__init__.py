from .user import user_bp

def register_blueprints(app):
    app.register_blueprint(user_bp,url_prefix='/user')
    