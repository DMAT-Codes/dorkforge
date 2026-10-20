from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import config_map
import os

db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)

    config_obj = config_map.get(config_name, config_map['default'])
    app.config.from_object(config_obj)

    db.init_app(app)

    # Import models so SQLAlchemy registers them
    from app import models  # noqa: F401

    # Create tables and seed template data
    with app.app_context():
        db.create_all()
        from app.services.template_service import seed_templates
        seed_templates()

    # Register blueprints
    from app.routes import main, builder, ai, templates, history, operators, about

    app.register_blueprint(main.bp)
    app.register_blueprint(builder.bp)
    app.register_blueprint(ai.bp)
    app.register_blueprint(templates.bp)
    app.register_blueprint(history.bp)
    app.register_blueprint(operators.bp)
    app.register_blueprint(about.bp)

    return app