from flask import Flask, render_template, request, redirect, url_for
from todo_logic import db, Todo 

app = Flask(__name__)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"

# Initialize db with this Flask app
db.init_app(app)

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        task_content = request.form["content"]
        new_task = Todo(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for("index"))
        except Exception as e:
            return f"Error adding task: {e}"
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template("index.html", tasks=tasks)

@app.route("/delete/<int:id>")
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
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
    return redirect(url_for("index"))
    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
