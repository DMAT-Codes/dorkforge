from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from app.config import config_map
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    config_obj = config_map.get(config_name, config_map['default'])
    app.config.from_object(config_obj)
    
    db.init_app(app)
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' 
    login_manager.login_message_category = 'info'

    from app import models

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        from app.services.template_service import seed_templates
        seed_templates()

    from app.routes import main, builder, ai, templates, history, operators, about, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(builder.bp)
    app.register_blueprint(ai.bp)
    app.register_blueprint(templates.bp)
    app.register_blueprint(history.bp)
    app.register_blueprint(operators.bp)
    app.register_blueprint(about.bp)
    app.register_blueprint(auth.bp)

    # --- GLOBAL AUTHENTICATION GATE ---
    @app.before_request
    def require_login():
        # Allow access to static files, login, and register pages without logging in
        allowed_endpoints = ['auth.login', 'auth.register', 'static']
        
        # If the user is not logged in and tries to access any other page, redirect to login
        if not current_user.is_authenticated and request.endpoint not in allowed_endpoints:
            return redirect(url_for('auth.login'))

    return app