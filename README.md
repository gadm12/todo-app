## To-Do App (v2.1 Flask)

* A simple web-based **To-Do application built using Flask**.
* This version improves on v2.0 by adding a **due date feature**, **database integration**, and an improved **task table layout**.

---

## Features

- Implemented column-based sorting
- Update task and update task due date
- Added # numbering column
- Add, view, and mark **and unmark** tasks as complete
- **Set a due date** for each task  
- Tasks display both **added date** and **due date**
- Clean and responsive table layout  
- Flash message feedback for user actions  
- Flask + SQLAlchemy database integration (SQLite)

--- 

## Tech Stack

- Python 3
- Flask
- HTML / Jinja2 Templates
- CSS (no JavaScript required)

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
    pip install flask flask_sqlalchemy
    ```

4. Initialize or upgrade the database

    ```bash
    flask shell
    >>> from models import db
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
* Allow task editing (content and due date)  
* Sort tasks by due date or completion status  
* Add user authentication for multiple users

---

## License

This project is open-source and available under the MIT License.

---

## Version 

**v2.1- Flask with Database & Due Dates**

---

## Author

**Mohamed Gad**

---
