## To-Do App (v3.0 Flask)

- A modern, secure To-Do web application built with Flask — featuring user registration, login, password hashing, personal task management, and now image upload with OCR (text extraction).

---

## What's New in v2.3

- This version builds on v2.2 with the addition of:

  - Image Uploads — users can upload screenshots of their schedules.
  - OCR Integration — the app uses Tesseract OCR to extract text from uploaded images.
  - Temporary File Storage — uploaded images are saved in a secure uploads/ directory.
  - Improved Access Control — uploads and tasks are linked to each logged-in user.
  - Enhanced Flash Messages — consistent design and categorized alerts (success, danger, info).

---

## Features

- User Accounts
  - Register, log in, and log out securely
  - Passwords hashed with Flask-Bcrypt
  - Each user has their own private to-do list
- Task Management
  - Add, update, delete tasks
  - Mark and unmark tasks as complete
  - Set optional due dates
  - Flash messages for user actions
  - Task sorting by:
    - Created date
    - Due date
    - Completion status
- Image Upload & OCR
  - Upload a screenshot of your schedule or notes
  - Extract text using pytesseract and OpenCV
  - Output is processed and displayed via flash messages
  - Supports file types: .png, .jpg, .jpeg, .gif
- Interface
  - Responsive layout with a clean, minimal UI
  - Displays both added and due dates
  - Supports ascending/descending sorting

---

## Tech Stack

- Backend: Python 3, Flask
- Database: SQLite (via SQLAlchemy ORM)
- Auth: Flask-Login, Flask-Bcrypt
- OCR & Image Processing: pytesseract, OpenCV
- Frontend: HTML + Jinja2 Templates, CSS

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
   pip install flask flask_sqlalchemy flask_bcrypt flask_login pytesseract opencv-python

   ```

4. Configure Tesseract Path

- Ensure you have Tesseract OCR installed.
- If using Windows, verify this path exists or update it in app.py:

  ```bash
  pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
  ```

5. Initialize or upgrade the database

   ```bash
   flask shell
   >>> from models import app, db
   >>> with app.app_context():
   >>> db.create_all()
   >>> exit()
   ```

6. Run the app

   ```bash
   python app.py
   ```

Then open your browser at: http://127.0.0.1:5000/

---

## Future Plans

- Display extracted OCR text in the UI
- Automatically convert recognized text into tasks
- Highlight overdue tasks
- Password reset and profile management
- Cloud deployment (Render, Railway, or Fly.io)

---

## License

This project is open-source and available under the MIT License.

---

## Version

**v3.0 — Flask with Authentication, Image Uploads, and OCR Integration**

---

## Author

**Mohamed Gad**

---
