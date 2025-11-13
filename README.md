## To-Do App (v2.3 Flask)

- A modern, secure To-Do web application built with Flask — featuring user registration, login, password hashing, personal task management, and now **image upload + OCR schedule extraction** powered by EasyOCR and OpenCV.

---

## What's New in v2.3

- This version builds on v2.2 with major new functionality:

### **Image Uploads**

- Users can upload screenshots of their weekly work schedules.

### **OCR Integration (EasyOCR + OpenCV)**

- Uploaded images are processed using:
  - **EasyOCR** for text extraction
  - **OpenCV** for preprocessing, thresholding, and layout detection
  - Automatic row + column grouping
  - Smart day/time detection for schedules

### **Temporary Upload Handling**

- Images are saved to an `uploads/` directory using secure filenames.

### **Improved Access Control**

- Uploads and parsing are only available to logged-in users.

### 💬 **Better Flash Messages**

- Unified styling across login, register, and dashboard pages.

---

## Features

### User Accounts

- Secure registration and login
- Password hashing using Flask-Bcrypt
- Each user has a personal to-do list
- Session-based authentication (Flask-Login)

### Task Management

- Add, update, delete tasks
- Mark complete / unmark complete
- Optional due dates
- Sorting by:
  - Date created
  - Due date
  - Completion status
- Clean UI + categorized flash messages

### Image Upload + OCR Parsing (NEW)

- Upload schedule screenshots (`.png`, `.jpg`, `.jpeg`, `.gif`)
- Automatic detection of:
  - Days of the week
  - Time ranges
  - “Not Scheduled” indicators
- Full preprocessing pipeline:
  - Grayscale + thresholding
  - Region detection
  - Row grouping
- Parsed schedule printed to terminal for now

### Interface

- Clean, modern, responsive layout
- Consistent alert styling across pages
- Welcome banner + navbar UI improvements

---

## Tech Stack

- **Backend:** Python 3, Flask
- **Database:** SQLite (SQLAlchemy ORM)
- **Authentication:** Flask-Login, Flask-Bcrypt
- **OCR Engine:** EasyOCR
- **Image Processing:** OpenCV (cv2)
- **Frontend:** HTML + Jinja2, CSS

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

- Display parsed OCR schedules directly in the dashboard
- Auto-convert schedule times into tasks
- Highlight overdue tasks visually
- Password reset feature
- User profile settings
- Deploy to Render, Railway, Fly.io, or Docker image

---

## License

This project is open-source and available under the MIT License.

---

## Version

**v2.3 — Flask with Authentication, Image Uploads, and OCR Integration**

---

## Author

**Mohamed Gad**

---
