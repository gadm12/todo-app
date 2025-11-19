# To-Do App (v3.1 Flask Web App)

A modern productivity app featuring user authentication, task management, weekly schedule OCR parsing, and now a **visual schedule viewer** that displays parsed shifts in a clean table format.

<p align="center">
  <img src="https://img.shields.io/badge/Flask-v2.3-blue" />
  <img src="https://img.shields.io/badge/Python-3.10+-yellow" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
  <img src="https://img.shields.io/badge/OCR-EasyOCR-red" />
  <img src="https://img.shields.io/badge/OpenCV-Image%20Processing-purple" />
  <img src="https://img.shields.io/badge/SQLAlchemy-ORM-orange" />
</p>

---

# 🚀 What's New in v3.1

### ✅ **New: View Schedule Page**

After uploading a schedule screenshot, users are now redirected to a **Schedule Viewer** showing:

- **Day of the week**
- **Actual calendar date**
- **Extracted shift hours** (e.g., `2 AM – 11 AM`)
- Clean table UI rendered directly in the browser

### 🎯 **Improved OCR Parsing Engine**

The updated parser includes:

- Better cleaning of OCR output
- Fixes common mistakes (e.g., `Iam → 11am`, `1 am → 1am`, `Oam → 0am`)
- Smarter grouping of text boxes
- Improved day/time detection accuracy

This upgrade dramatically reduces incorrect readings.

### 🟦💼🟩🌴 **"Day Off" Recognition**

If a day is marked as:

- "Not Scheduled"
- "Off"
- "—"
- Blank

It now **appears as “Day Off” in the schedule table**.

In the upcoming update (v3.2), off-days will be green, work shifts blue.

### 📁 Secure Temporary Storage

- Uploaded screenshots stored with `secure_filename()`
- Parsed results stored as JSON per user
- Preprocessing pipeline improved for uniform OCR results

---

# ✨ Features

## 👤 User Accounts

- User registration & login
- Passwords hashed using **Flask-Bcrypt**
- Personal tasks & personal schedules
- Authentication handled via **Flask-Login**

---

## ✅ Task Management

- Add / edit / delete tasks
- Mark complete / unmark
- Optional due dates
- Sorting by:
  - Creation date
  - Due date
  - Completion status
- Clean UI with improved flash messages

---

# 🖼️ Image Upload + OCR Schedule Parsing

### Supported Formats

`.png`, `.jpg`, `.jpeg`, `.gif`

### OCR Processing Pipeline

1. OpenCV preprocessing
   - Grayscale
   - Thresholding
   - Crop/resize normalization
2. EasyOCR extraction
3. Smart grouping + cleanup
4. Fix common OCR typos
5. Create structured schedule

---

### NEW in v3.1

- Parsed schedule displayed in a beautiful table
- Each day includes:
  - Weekday (Mon–Sun)
  - Actual date
  - Work shift or Day Off

---

## 🖥️ Interface

- Fully responsive layout
- Clean, responsive layout
- Custom login & signup UI
- Modern navbar
- Uniform styling across all pages
- Unified flash message styling

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

## ⚙️ Setup Instructions

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

## 🧭 Future Plans

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

## 📄 License

This project is open-source and available under the MIT License.

---

## 🏷️ Version

**v3.1 — Schedule Viewer Update, Improved OCR Parsing, Day-Off Detection**

---

## 👨‍💻 Author

**Mohamed Gad**

---
