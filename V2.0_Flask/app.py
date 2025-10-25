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
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return "<Task %r>" % self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    
    return render_template("index.html")

if __name__ == "__main__":
    
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
#inside python repl write the following to create the .db file
#from app import app, db
#with app.app_context():
#    db.create_all()
#hit enter again
#to check the file path do the following inside python repl
#import os
#print(os.getcwd())