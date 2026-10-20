from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    """Application user (reserved for future authentication)."""
    __tablename__ = 'users'

    User_ID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(80), unique=True, nullable=False)
    Password_Hash = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    Created_At = db.Column(db.DateTime, default=datetime.utcnow)

    saved_queries = db.relationship(
        'SavedQuery',
        backref='owner',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def set_password(self, password):
        self.Password_Hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.Password_Hash, password)

    def __repr__(self):
        return f'<User {self.Username}>'


class Template(db.Model):
    """Pre-defined dork template library."""
    __tablename__ = 'templates'

    Template_ID = db.Column(db.Integer, primary_key=True)
    Category = db.Column(db.String(80), nullable=False)
    Query_String = db.Column(db.Text, nullable=False)
    Explanation = db.Column(db.Text)
    
    # NOTE: Add these two fields to your report!
    Name = db.Column(db.String(120), nullable=False)
    Security_Context = db.Column(db.Text)

    def __repr__(self):
        return f'<Template {self.Name}>'


class SavedQuery(db.Model):
    """A query saved by a user (User_ID nullable for anonymous use)."""
    __tablename__ = 'saved_queries'

    Query_ID = db.Column(db.Integer, primary_key=True)
    User_ID = db.Column(db.Integer, db.ForeignKey('users.User_ID'), nullable=True)
    Query_String = db.Column(db.Text, nullable=False)
    Title = db.Column(db.String(120))
    Notes = db.Column(db.Text)
    Date_Saved = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SavedQuery {self.Query_ID}>'