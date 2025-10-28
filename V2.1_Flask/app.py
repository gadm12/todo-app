from flask import Flask, render_template, request, redirect, url_for, flash
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
        tasks = Todo.query.order_by(Todo.date_created.desc()).all()
        return render_template("index.html", tasks=tasks)

        
        

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
    
    

@app.route("/update/<int:id>", methods=["POST", "GET"])
def update(id):
    
    task = Todo.query.get_or_404(id)
    
    
    
    if request.method == "POST":
        task.content = request.form["content"]
        try:
            db.session.commit()
            flash("Task has been updated")
            return redirect(url_for("index"))
        except Exception as e:
            return f"Error updating task: {e}"
    else:
        return render_template("update.html", task=task)
    

    
@app.route("/complete/<int:id>")
def complete(id):
    
    task=Todo.query.get_or_404(id)
    
    
    task.completed=1
    db.session.commit()
    flash("Task has been marked complete")
    return redirect(url_for("index"))
    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
