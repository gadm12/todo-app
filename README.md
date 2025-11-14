## To-Do App (v3.0 Flask Web App)

- A modern productivity app featuring user authentication, task management, and automated schedule parsing via OCR.

<p align="center"> <img src="https://img.shields.io/badge/Flask-v2.3-blue" /> <img src="https://img.shields.io/badge/Python-3.10+-yellow" /> <img src="https://img.shields.io/badge/License-MIT-green" /> <img src="https://img.shields.io/badge/OCR-EasyOCR-red" /> <img src="https://img.shields.io/badge/SQLAlchemy-ORM-orange" /> </p>

---

### 📸 Image Uploads

Users can now upload screenshots of their weekly work schedules.

### OCR Integration (EasyOCR + OpenCV)

Uploaded images are automatically processed with:

- **EasyOCR** — text extraction
- **OpenCV** — preprocessing (grayscale, thresholding, cropping)
- Automatic table/row detection
- Smart identification of:
  - Days of the week
  - Shift time ranges
  - “Off” / “Not Scheduled” entries

### Schedule Storage

- Parsed schedule JSON saved individually for each user
- Uploaded images stored securely with `secure_filename()`

### Improved Access Control

- Only logged-in users can upload/view schedules

### Enhanced Flash Messages

- Unified, color-coded alert system across all pages

---

# Features

## User Accounts

- Register, log in, log out
- Passwords hashed via **Flask-Bcrypt**
- Private tasks & private schedules per user
- Session management via **Flask-Login**

---

## Task Management

- Add, update, delete tasks
- Mark complete / unmark incomplete
- Optional due dates
- Sorting options:
  - Creation date
  - Due date
  - Completed status
- Clean, modern UI
- Contextual flash messages

---

## Image Upload + OCR Schedule Parsing (NEW)

- Supports `.png`, `.jpg`, `.jpeg`, `.gif`
- Automatically extracts weekly schedule info:
  - Day → Time Range
  - “Not Scheduled” handling
- Saves:
  - Uploaded image
  - Week start date
  - Parsed JSON schedule
- Debug mode prints extracted schedule to console

---

## Interface

- Clean, responsive layout
- Custom login & signup UI
- Modern navbar
- Uniform styling across all pages

---

# 🛠 Tech Stack

| Layer            | Technology                |
| ---------------- | ------------------------- |
| Backend          | Flask (Python 3)          |
| Database         | SQLite (SQLAlchemy ORM)   |
| Auth             | Flask-Login, Flask-Bcrypt |
| OCR              | EasyOCR                   |
| Image Processing | OpenCV (cv2)              |
| Frontend         | HTML, Jinja2, CSS         |

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
   pip install flask flask_sqlalchemy flask_bcrypt flask_login easyocr opencv-python

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

- Display parsed schedules directly in the UI
- Export schedules to Apple/Google Calendar
- Auto-convert shifts into tasks
- Highlight overdue tasks
- Password reset system
- User profile settings
- Deployment to:
  - Render
  - Railway
  - Fly.io
  - Docker

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
