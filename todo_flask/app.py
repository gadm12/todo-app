from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from models import db, User, Todo, Schedule
from datetime import datetime, timedelta
import os
import io
import re
from ics import Calendar, Event
from werkzeug.utils import secure_filename
from parser import ScheduleParser

app = Flask(__name__)


# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "doors"
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}

# Initialize db with this Flask app
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

print("Loading OCR model (this may take a moment)...")
schedule_parser = ScheduleParser()
print("OCR Model loaded. Starting server.")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/register", methods=["POST", "GET"])
def register():

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if not username or not email or not password:
            flash("All fields are required. Please try again.", "danger")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return render_template("register.html")

        existing_user_email = User.query.filter_by(email=email).first()
        if existing_user_email:
            flash("That email is already in use. Please choose another.", "danger")
            return render_template("register.html")

        existing_user_name = User.query.filter_by(username=username).first()
        if existing_user_name:
            flash("That username is already taken. Please choose another.", "danger")
            return render_template("register.html")

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        new_user = User(username=username, email=email, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! You can now log in.", "success")

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("index"))

        else:
            flash("Login failed. Check email and password.", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():

    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/", methods=["POST", "GET"])
@login_required
def index():
    current_time = datetime.now().strftime("%A, %B %d, %Y - %I:%M %p")

    if request.method == "POST":
        # --- Get ALL potential form data ---
        task_content = request.form["content"].strip()
        due_date_str = request.form.get("due")
        file = request.files.get("screenshot")
        start_date_str = request.form.get("schedule_start_date")

        if file and file.filename != "" and start_date_str:

            filename = secure_filename(file.filename)
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(save_path)

            try:

                parsed_schedule = schedule_parser.parse_schedule(save_path, debug=True)

                print(f"Type of start_date_str: {type(start_date_str)}")
                print(f"Value: {start_date_str}")

                # Convert string to date
                week_start = datetime.strptime(start_date_str, "%Y-%m-%d").date()

                print(f"Type of week_start: {type(week_start)}")
                print(f"Value: {week_start}")

                new_schedule = Schedule(
                    user_id=current_user.id,
                    week_start_date=week_start,
                    image_filename=filename,
                    parsed_data=parsed_schedule,
                )
                db.session.add(new_schedule)
                db.session.commit()

                flash("Schedule parsed and saved successfully!", "success")
                return redirect(url_for("view_schedule", schedule_id=new_schedule.id))

            except Exception as e:
                flash(f"Error parsing image: {e}", "danger")

            return redirect(url_for("index"))

        elif task_content:
            if due_date_str:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            else:
                due_date = None

            new_task = Todo(content=task_content, due=due_date, user_id=current_user.id)

            try:
                db.session.add(new_task)
                db.session.commit()
                flash("Task added successfully", "success")
            except Exception as e:
                print(f"Error adding task: {e}")
                flash("There was an issue adding your task", "danger")

            return redirect(url_for("index"))

        else:
            flash("Please add a task or upload a file with its start date.", "danger")
            return redirect(url_for("index"))

    else:
        sort = request.args.get("sort", "created")
        order = request.args.get("order", "asc")

        query = Todo.query.filter_by(user_id=current_user.id)

        if sort == "due":
            query = query.order_by(
                Todo.due.desc() if order == "desc" else Todo.due.asc()
            )
        elif sort == "completed":
            query = query.order_by(
                Todo.completed.desc() if order == "desc" else Todo.completed.asc()
            )
        else:
            query = query.order_by(
                Todo.date_created.desc() if order == "desc" else Todo.date_created.asc()
            )

        tasks = query.all()
        return render_template(
            "index.html", tasks=tasks, sort=sort, order=order, current_time=current_time
        )


@app.route("/schedule/<int:schedule_id>")
@login_required
def view_schedule(schedule_id):

    schedule = Schedule.query.filter_by(
        id=schedule_id, user_id=current_user.id
    ).first_or_404()

    days_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    return render_template(
        "view_schedule.html", schedule=schedule, days_order=days_order
    )


@app.route("/schedule/<int:schedule_id>/export")
@login_required
def export_ics(schedule_id):
    schedule = Schedule.query.filter_by(
        id=schedule_id, user_id=current_user.id
    ).first_or_404

    cal = Calendar()

    days_map = {
        "Mon": 0,
        "Tue": 1,
        "Wed": 2,
        "Thu": 3,
        "Fri": 4,
        "Sat": 5,
        "Sun": 6,
    }

    for day, time_range in schedule.parsed_data.items():
        if time_range == "Not Schedule":
            continue

        match = re.search(r"(\d+)\s*(am|pm)\s*-\s*(\d+)\s*(am|pm)", time_range, re.I)

        if not match:
            continue

        start_hour = int(match.group(1))
        start_period = match.group(2).lower()
        end_hour = int(match.group(3))
        end_period = match.group(4).lower()

        if start_period == "pm" and start_hour != 12:
            start_hour += 12
        if end_period == "pm" and end_hour != 12:
            end_hour += 12

        event_date = schedule.week_start_date + timedelta(days=days_map[day])

        e = Event()
        e.name = "Work Shift"
        e.begin = datetime.combine(event_date, datetime.min.time()).replace(
            hour=start_hour
        )
        e.end = datetime.combine(event_date, datetime.min.time()).replace(hour=end_hour)
        cal.events.add(e)

    ics_file = io.BytesIO()
    ics_file.write(str(cal).encode("utf-8"))
    ics_file.seek(0)

    return send_file(
        ics_file,
        mimetype="text/calendar",
        as_attachment=True,
        download_name=f"schedule_{schedule.week_start_date}.ics",
    )


@app.route("/update/<int:id>", methods=["POST", "GET"])
@login_required
def update(id):

    task = Todo.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        task.content = request.form["content"]

        due_str = request.form["due"]

        if due_str:
            task.due = datetime.strptime(due_str, "%Y-%m-%d").date()
        else:
            task.due = None

        try:
            db.session.commit()
            flash("Task has been updated", "info")
            return redirect(url_for("index"))
        except Exception as e:
            db.session.rollback()
            return f"Error updating task: {e}"
    else:
        return render_template("update.html", task=task)


@app.route("/delete/<int:id>")
@login_required
def delete(id):
    task_to_delete = Todo.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    flash("Task has been deleted", "danger")
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url_for("index"))
    except Exception as e:
        return f"Error deleting task: {e}"


@app.route("/complete/<int:id>")
@login_required
def complete(id):

    task = Todo.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    task.completed = 1
    db.session.commit()
    flash("Task has been marked complete", "info")
    return redirect(url_for("index"))


@app.route("/unmark/<int:id>")
@login_required
def unmark(id):

    unmark_task = Todo.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    unmark_task.completed = 0
    db.session.commit()
    flash("Task has been marked as incomplete", "danger")
    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
