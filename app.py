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
from parser import ScheduleParser
from datetime import datetime, timedelta, time
from ics import Calendar, Event
from werkzeug.utils import secure_filename
import os
import io
import re
import pytz
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import config


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


@app.route("/auth", methods=["GET", "POST"])
def auth():
    if request.method == "POST":
        # Check which form was submitted
        if "login" in request.form or request.referrer.endswith("#login"):
            # Handle login
            email = request.form["email"]
            password = request.form["password"]
            # ... login logic
            return redirect(url_for("index"))
        else:
            # Handle registration
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            # ... register logic
            flash("Account created! Please log in.", "success")
            return redirect(url_for("auth") + "#login")

    return render_template("auth_tabs.html")


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

                week_start = datetime.strptime(start_date_str, "%Y-%m-%d").date()

                print(f"Week starts on: {week_start} ({week_start.strftime('%A')})")

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

    week_start_weekday = schedule.week_start_date.weekday()
    day_offsets = {}
    for i, day in enumerate(days_order):
        day_weekday = i
        offset = (day_weekday - week_start_weekday) % 7
        day_offsets[day] = offset

    return render_template(
        "view_schedule.html",
        schedule=schedule,
        days_order=days_order,
        day_offsets=day_offsets,
        timedelta=timedelta,
    )


@app.route("/schedule/<int:schedule_id>/export")
@login_required
def export_ics(schedule_id):
    from ics import Calendar, Event
    from datetime import datetime, timedelta, time
    import re
    import io
    from flask import send_file
    import pytz

    schedule = Schedule.query.filter_by(
        id=schedule_id, user_id=current_user.id
    ).first_or_404()

    cal = Calendar()
    tz = pytz.timezone("America/Chicago")  # Adjust to your timezone

    week_start_weekday = schedule.week_start_date.weekday()
    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    days_map = {}
    for i, day in enumerate(days_of_week):
        day_weekday = i
        offset = (day_weekday - week_start_weekday) % 7
        days_map[day] = offset

    for day, time_range in schedule.parsed_data.items():
        event_date = schedule.week_start_date + timedelta(days=days_map[day])

        if time_range == "Not Scheduled":
            # Create a timed "Day Off" event (5am - 3pm)
            e = Event()
            e.name = "Day Off 🌴"
            start_dt = tz.localize(datetime.combine(event_date, time(hour=2, minute=0)))
            end_dt = tz.localize(datetime.combine(event_date, time(hour=11, minute=0)))
            e.begin = start_dt
            e.end = end_dt
            cal.events.add(e)
            continue

        # Parse work shift times
        match = re.search(r"(\d+)(am|pm)\s*-\s*(\d+)(am|pm)", time_range, re.I)

        if not match:
            print(f"Warning: Could not parse time for {day}: {time_range}")
            continue

        start_hour = int(match.group(1))
        start_period = match.group(2).lower()
        end_hour = int(match.group(3))
        end_period = match.group(4).lower()

        # Convert to 24-hour
        if start_period == "pm" and start_hour != 12:
            start_hour += 12
        elif start_period == "am" and start_hour == 12:
            start_hour = 0

        if end_period == "pm" and end_hour != 12:
            end_hour += 12
        elif end_period == "am" and end_hour == 12:
            end_hour = 0

        # Create start datetime
        start_dt = tz.localize(datetime.combine(event_date, time(hour=start_hour)))

        # Check if shift crosses midnight (end hour is earlier than start hour)
        if end_hour < start_hour:
            # Shift goes to next day
            end_date = event_date + timedelta(days=1)
            end_dt = tz.localize(datetime.combine(end_date, time(hour=end_hour)))
        else:
            # Shift ends same day
            end_dt = tz.localize(datetime.combine(event_date, time(hour=end_hour)))

        # Create work shift event
        e = Event()
        e.name = "Work Shift 💼"
        e.begin = start_dt
        e.end = end_dt

        print(f"{day}: {start_dt} → {end_dt}")  # Debug

        cal.events.add(e)

    # Generate ICS file
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


@app.route("/connect-google-calendar")
@login_required
def connect_google_calendar():
    """Initiate Google OAuth flow"""
    flow = Flow.from_client_secrets_file(
        config.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=config.SCOPES,
        redirect_uri=url_for("oauth2callback", _external=True),
    )

    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )

    # Store state in session for verification
    from flask import session

    session["state"] = state

    return redirect(authorization_url)


@app.route("/oauth2callback")
@login_required
def oauth2callback():
    """Handle OAuth callback from Google"""
    from flask import session

    state = session["state"]

    flow = Flow.from_client_secrets_file(
        config.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=config.SCOPES,
        state=state,
        redirect_uri=url_for("oauth2callback", _external=True),
    )

    # Get authorization response
    flow.fetch_token(authorization_response=request.url)

    # Store credentials in database
    credentials = flow.credentials
    current_user.google_calendar_token = credentials.to_json()
    current_user.google_calendar_connected = True
    db.session.commit()

    flash("Google Calendar connected successfully! 🎉", "success")
    return redirect(url_for("index"))


@app.route("/schedule/<int:schedule_id>/add-to-google-calendar")
@login_required
def add_to_google_calendar(schedule_id):
    """Add schedule directly to Google Calendar"""

    # Check if user has connected Google Calendar
    if not current_user.google_calendar_connected:
        flash("Please connect your Google Calendar first!", "danger")
        return redirect(url_for("view_schedule", schedule_id=schedule_id))

    # Get the schedule
    schedule = Schedule.query.filter_by(
        id=schedule_id, user_id=current_user.id
    ).first_or_404()

    try:

        # Load credentials from database
        credentials = Credentials.from_authorized_user_info(
            json.loads(current_user.google_calendar_token)
        )

        # Build Calendar API service
        service = build("calendar", "v3", credentials=credentials)

        # Timezone
        tz = pytz.timezone("America/Chicago")

        # Calculate day offsets
        week_start_weekday = schedule.week_start_date.weekday()
        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        days_map = {}
        for i, day in enumerate(days_of_week):
            day_weekday = i
            offset = (day_weekday - week_start_weekday) % 7
            days_map[day] = offset

        events_created = 0

        for day, time_range in schedule.parsed_data.items():

            event_date = schedule.week_start_date + timedelta(days=days_map[day])

            if time_range == "Not Scheduled":
                # Create Day Off event
                event = {
                    "summary": "Day Off 🌴",
                    "start": {
                        "date": event_date.isoformat(),
                        "timeZone": "America/Chicago",
                    },
                    "end": {
                        "date": (event_date + timedelta(days=1)).isoformat(),
                        "timeZone": "America/Chicago",
                    },
                    "colorId": "10",  # Green
                }

                service.events().insert(calendarId="primary", body=event).execute()
                events_created += 1
                continue

            # Parse work shift
            match = re.search(r"(\d+)(am|pm)\s*-\s*(\d+)(am|pm)", time_range, re.I)

            if not match:
                continue

            start_hour = int(match.group(1))
            start_period = match.group(2).lower()
            end_hour = int(match.group(3))
            end_period = match.group(4).lower()

            # Convert to 24-hour
            if start_period == "pm" and start_hour != 12:
                start_hour += 12
            elif start_period == "am" and start_hour == 12:
                start_hour = 0

            if end_period == "pm" and end_hour != 12:
                end_hour += 12
            elif end_period == "am" and end_hour == 12:
                end_hour = 0

            # Check if crosses midnight
            if end_hour < start_hour:
                end_date = event_date + timedelta(days=1)
            else:
                end_date = event_date

            # Create work shift event
            start_dt = tz.localize(
                datetime.combine(event_date, datetime.min.time()).replace(
                    hour=start_hour
                )
            )
            end_dt = tz.localize(
                datetime.combine(end_date, datetime.min.time()).replace(hour=end_hour)
            )

            event = {
                "summary": "Work Shift 💼",
                "description": "Grocery Replenishment Specialist\nStore #1602",
                "start": {
                    "dateTime": start_dt.isoformat(),
                    "timeZone": "America/Chicago",
                },
                "end": {
                    "dateTime": end_dt.isoformat(),
                    "timeZone": "America/Chicago",
                },
                "colorId": "9",  # Blue
            }

            service.events().insert(calendarId="primary", body=event).execute()

            events_created += 1

        # THIS IS NOW OUTSIDE THE LOOP
        flash(
            f"Successfully added {events_created} events to your Google Calendar! 🎉",
            "success",
        )
        return redirect(url_for("view_schedule", schedule_id=schedule_id))

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        flash(f"Error adding to Google Calendar: {str(e)}", "danger")
        return redirect(url_for("view_schedule", schedule_id=schedule_id))


@app.route("/disconnect-google-calendar")
@login_required
def disconnect_google_calendar():
    """Disconnect Google Calendar"""
    current_user.google_calendar_token = None
    current_user.google_calendar_connected = False
    db.session.commit()

    flash("Google Calendar disconnected.", "info")
    return redirect(url_for("index"))


@app.route("/schedules")
@login_required
def schedules_list():
    """Show all schedules for the current user"""
    schedules = (
        Schedule.query.filter_by(user_id=current_user.id)
        .order_by(Schedule.created_at.desc())
        .all()
    )
    return render_template("schedules.html", schedules=schedules)


@app.route("/schedule/<int:schedule_id>/delete", methods=["POST"])
@login_required
def delete_schedule(schedule_id):
    """Delete a schedule"""
    schedule = Schedule.query.filter_by(
        id=schedule_id, user_id=current_user.id
    ).first_or_404()
    db.session.delete(schedule)
    db.session.commit()
    flash("Schedule deleted successfully", "info")
    return redirect(url_for("schedules_list"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "False") == "True"
    app.run(host="0.0.0.0", port=port, debug=debug)
