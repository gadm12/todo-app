from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone


db = SQLAlchemy()


# Database model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # nullable so it wouldn't accept a blank task
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    due = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"<Task {self.id}>"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    # Google Calendar integration
    # Store OAuth2 credentials as JSON
    google_calendar_token = db.Column(db.Text, nullable=True)
    google_calendar_connected = db.Column(db.Boolean, default=False)

    # Relationship to Todo and Schedule
    todos = db.relationship("Todo", backref="user", lazy=True)
    schedules = db.relationship("Schedule", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    week_start_date = db.Column(db.Date, nullable=False)
    image_filename = db.Column(db.String(200))
    parsed_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Schedule {self.id} - Week of {self.week_start_date}>"
