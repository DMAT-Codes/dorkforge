from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    """Application user (reserved for future authentication)."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    saved_queries = db.relationship(
        'SavedQuery',
        backref='owner',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Template(db.Model):
    """Pre-defined dork template library."""
    __tablename__ = 'templates'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    query_string = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text)
    security_context = db.Column(db.Text)

    def __repr__(self):
        return f'<Template {self.name}>'


class SavedQuery(db.Model):
    """A query saved by a user (user_id nullable for anonymous use)."""
    __tablename__ = 'saved_queries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    query_string = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(120))
    notes = db.Column(db.Text)
    date_saved = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SavedQuery {self.id}>'