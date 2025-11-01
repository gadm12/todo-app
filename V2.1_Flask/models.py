from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin 
from datetime import datetime, timezone


# Create SQLAlchemy instance (no app yet)
db = SQLAlchemy()

# Database model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #nullable so it wouldn't accept a blank task
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    due = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"<Task {self.id}>"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    todos = db.relationship('Todo', backref='user', lazy=True)
    
    def __repr__(self):
        return f"<User {self.username}>"