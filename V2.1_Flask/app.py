from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin
from models  import db, Todo 
from datetime import datetime



app = Flask(__name__)
app.secret_key = "windows"

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize db with this Flask app
db.init_app(app)

@app.route("/", methods=["POST", "GET"])
def index():
    current_time = datetime.now().strftime("%A, %B %d, %Y - %I:%M %p")
    if request.method == "POST":
        task_content = request.form["content"].strip()
        due_date_str=request.form.get("due")
        if not task_content:
            flash("Task cannot be empty!")
            return redirect(url_for("index"))
        
        if due_date_str:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        else:
            due_date = None
        
        new_task = Todo(content=task_content, due=due_date)
        
        try:
            db.session.add(new_task)
            db.session.commit()
            flash("Task added successfully")
            return redirect(url_for("index"))
        except Exception as e:
            print(f"Error adding task: {e}")
            return "There was an issue adding your task"
    else:
        sort = request.args.get("sort", "created")
        order = request.args.get("order","asc")
        
        query = Todo.query

        if sort == "due":
            query = Todo.query.order_by(Todo.due.desc() if order == "desc" else Todo.due.asc())
        elif sort == "completed":
            query = query = query.order_by(Todo.completed.desc() if order == "desc" else Todo.completed.asc())
        else:
            query = query.order_by(Todo.date_created.desc() if order == "desc" else Todo.date_created.asc())
            
        tasks= query.all()
        return render_template("index.html", tasks=tasks, sort=sort, order=order ,current_time=current_time)

        
@app.route("/update/<int:id>", methods=["POST", "GET"])
def update(id):
    
    task = Todo.query.get_or_404(id)
    
    if request.method == "POST":
        task.content = request.form["content"]
        
        due_str = request.form["due"]
        
        if due_str:  
            task.due = datetime.strptime(due_str, "%Y-%m-%d").date()
        else:
            task.due = None 
        
        try:
            db.session.commit()
            flash("Task has been updated")
            return redirect(url_for("index"))
        except Exception as e:
            db.session.rollback()
            return f"Error updating task: {e}"
    else:
        return render_template("update.html", task=task)        
        

@app.route("/delete/<int:id>")
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    flash("Task has been deleted")
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url_for("index"))
    except Exception as e:
        return f"Error deleting task: {e}"
    
    

    

    
@app.route("/complete/<int:id>")
def complete(id):
    
    task=Todo.query.get_or_404(id)
    
    
    task.completed=1
    db.session.commit()
    flash("Task has been marked complete")
    return redirect(url_for("index"))

@app.route("/unmark/<int:id>")
def unmark(id):
    
    unmark_task = Todo.query.get_or_404(id)
    
    unmark_task.completed = 0
    db.session.commit()
    flash("Task has been marked as incomplete")
    return redirect(url_for("index"))
    
    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
