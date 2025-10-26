from flask import Flask, render_template, request, url_for,session, redirect
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

@app.route("/", methods=["POST", "GET"])
def index():
    
    if request.method == "POST":
        task_content = request.form["content"]
        new_task=Todo(content=task_content)
    
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for("index"))
        
        except Exception as e:
            print(f"Error adding task: {e}")
            return "There was an issue adding your task"
        
    
    else:
        tasks=Todo.query.order_by(Todo.date_created).all()
        return render_template("index.html", tasks=tasks)

@app.route("/delete/<int:id>")

def delete(id):
    
    task_to_delete = Todo.query.get_or_404(id)
    
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url_for("index"))
    except Exception as e:
        print(f"Error deleting a task: {e}")
        return "There was an issue deleting your task"
    
@app.route("/update/<int:id>",methods=["POST", "GET"])
def update(id):
    
    task=Todo.query.get_or_404(id)
    
    if request.method == "POST":
        task.content=request.form["content"]
        
        
    
        try:
    
            db.session.commit()
            return redirect(url_for("index"))
        
        except Exception as e:
            print(f"Error updating task: {e}")
            return "There was an issue with updating your task"
    
    else:
        return render_template("update.html", task=task)
    

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