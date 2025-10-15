# To-Do List CLI App

A simple **command-line To-Do List application** built with Python.
This project is designed as a beginner-friendly way to practice functions, file handling, and unit testing.

---

## Features (v1.1)

* Add multiple tasks at once
* Add due dates to tasks (with validation: YYYY-MM-DD)
* View all tasks with due date status (Overdue, Due Today, Upcoming)
* Mark tasks as completed
* Delete tasks
* Save and load tasks using JSON
* Clean and readable CLI output  

---

## Getting Started

### Prerequisites

* Python 3.8 or higher installed on your machine
* Git (optional, for version control)

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/gadm12/todo-cli-app.git
   cd todo-cli-app
   ```
2. Run the app:

   ```bash
   python to_do_list.py
   ```

---

## Usage

When you run the program, you can:

* Add tasks by typing their description.
* Optionally set a due date for each task.
* View your current tasks with status (completed or not) and and due-date status.
* Mark tasks as completed by selecting their number.
* Delete tasks by number.
* Save and load tasks automatically from `to_do_list.json`.

---

## Example Output

```
==============================
 Welcome to the To-Do App!
==============================

1. [ ] Buy groceries (Due: 2025-10-07 - Upcoming)
2. [✓] Finish homework (Due: 2025-10-02 - Overdue)
3. [ ] Call Mom (No due date)

Total tasks: 3

```

---

## Project Goals

* Practice breaking a project into milestones.
* Learn how to save and load data with JSON.
* Build testing habits with unit tests.
* Use Git branching and versioning effectively.
* Document progress clearly in GitHub.

---

## Future Improvements

* Add task priorities (High, Medium, Low)
* Organize tasks into categories
* Build a GUI (Tkinter or PySimpleGUI)
* Create a web app version (Flask or FastAPI)
* Add unit tests for core functions

---

## License

This project is open-source and available under the MIT License.

---

| Version | Date       | Changes                                                                 |
|----------|------------|--------------------------------------------------------------------------|
| **v1.1** | Oct 2025   | Added bulk task input, due date feature, improved CLI formatting.       |
| **v1.0** | Sep 2025   | Initial release with add, view, mark complete, delete, and save/load.   |



---

## Version 

**v1.1 - CLI Release**

---

## Author

**Mohamed Gad**

---
