from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    User_ID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(80), unique=True, nullable=False)
    Password_Hash = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    Created_At = db.Column(db.DateTime, default=datetime.utcnow)

    saved_queries = db.relationship('SavedQuery', backref='owner', lazy=True, cascade='all, delete-orphan')

    # Flask-Login requires an 'id' attribute
    @property
    def id(self):
        return self.User_ID

    def set_password(self, password):
        self.Password_Hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.Password_Hash, password)

    def __repr__(self):
        return f'<User {self.Username}>'


class Template(db.Model):
    __tablename__ = 'templates'
    Template_ID = db.Column(db.Integer, primary_key=True)
    Category = db.Column(db.String(80), nullable=False)
    Query_String = db.Column(db.Text, nullable=False)
    Explanation = db.Column(db.Text)
    Name = db.Column(db.String(120), nullable=False)
    Security_Context = db.Column(db.Text)


class SavedQuery(db.Model):
    __tablename__ = 'saved_queries'
    Query_ID = db.Column(db.Integer, primary_key=True)
    User_ID = db.Column(db.Integer, db.ForeignKey('users.User_ID'), nullable=True)
    Query_String = db.Column(db.Text, nullable=False)
    Title = db.Column(db.String(120))
    Notes = db.Column(db.Text)
    Date_Saved = db.Column(db.DateTime, default=datetime.utcnow)