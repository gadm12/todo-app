from flask_sqlalchemy import SQLAlchemy
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

    def __repr__(self):
        return f"<Task {self.id}>"
