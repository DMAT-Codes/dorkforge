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

    from app import models

    with app.app_context():
        db.create_all()
        
        # Seed Templates
        from app.services.template_service import seed_templates
        seed_templates()

        # Create a Guest User for Saved Queries (since there is no login yet)
        if not models.User.query.first():
            guest_user = models.User(
                Username='Guest', 
                Email='guest@dorkforge.local', 
                Password_Hash='not_required_yet'
            )
            db.session.add(guest_user)
            db.session.commit()

    from app.routes import main, builder, ai, templates, history, operators, about
    app.register_blueprint(main.bp)
    app.register_blueprint(builder.bp)
    app.register_blueprint(ai.bp)
    app.register_blueprint(templates.bp)
    app.register_blueprint(history.bp)
    app.register_blueprint(operators.bp)
    app.register_blueprint(about.bp)

    return app