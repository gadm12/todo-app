## To-Do App (v2.2 Flask)

* A modern, secure To-Do web application built with Flask, featuring user registration, login, password hashing, and personal task management.

* This version expands on earlier releases by adding:

    - User authentication (register/login/logout)
    - Secure password hashing using Flask-Bcrypt
    - User-specific task lists (each user sees only their own tasks)
    - Due date support and improved task management UI

---

## Features

* User Accounts
    * Register, log in, and log out securely
    * Passwords hashed with Flask-Bcrypt
    * Each user has their own private to-do list
* Task Management
    * Add, update, delete tasks
    * Mark and unmark tasks as complete
    * Set optional due dates
    * Flash messages for user actions
    * Task sorting by:
        * Created date
        * Due date
        * Completion status
* Interface
    * Responsive layout with a clean, minimal UI
    * Displays both added and due dates
    * Supports ascending/descending sorting

--- 

## Tech Stack

* Backend: Python 3, Flask
* Database: SQLite (via SQLAlchemy ORM)
* Auth: Flask-Login, Flask-Bcrypt
* Frontend: HTML + Jinja2 Templates, CSS

---

## Setup Instructions

1. Clone the repository

    ```bash
    git clone https://github.com/gadm12/todo-cli-app.git
    cd todo-app/v2.0_Flask
    ```


2. Create and activate a virtual environment

    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3. Install dependencies

    ```bash
    pip install flask flask_sqlalchemy flask_bcrypt flask_login
    ```

4. Initialize or upgrade the database

    ```bash
    flask shell
    >>> from models import app, db
    >>> with app.app_context():
    >>> db.create_all()
    >>> exit()
    ```

5. Run the app

    ```bash
    python app.py
    ```

Then open your browser at: http://127.0.0.1:5000/

---

## Future Plans

* Highlight overdue tasks
* Password reset functionality
* Profile management page
* Task search and filtering
* Deployment to a cloud platform (Render, Railway, etc.)

---

## License

This project is open-source and available under the MIT License.

---

## Version 

**v2.2 — Flask with User Authentication & Due Dates**

---

## Author

**Mohamed Gad**

---
