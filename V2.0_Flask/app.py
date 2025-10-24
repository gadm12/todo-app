from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone


app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #nullable: so user would not be able to create a blank task
    content = db.Column(db.String(200),nullable=False)
    completed = db.Column(db.Integer, default=0)
    data_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return "<Task %r>" % self.id

@app.route('/')
def index():
    
    return render_template("index.html")

if __name__ == "__main__":
    
    
    app.run(debug=True)