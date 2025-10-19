# Changelog

All notable changes to this project will be documented in this file.

---

## [v1.3] - 2025-10-19

### Added
- **Edit task** feature — allows users to update task description or due date.
- Implemented **search functionality** to find tasks by keyword.
- Added **due date** support for tasks with input validation (`YYYY-MM-DD`).
- Tasks now display their **due date status** (Overdue, Due Today, or Upcoming).
- Ability to add multiple tasks in one session.
- Confirmation prompt to continue adding tasks (`'y'` to continue, anything else to stop).
- Task counter message after adding multiple tasks.
- Improved code readability and structure for easier future updates.

### Changed
- Improved program structure with better **error handling** and **docstrings**.
- Refined CLI prompts for smoother user experience.
- Displayed task counts when loading and after updates.
- `add_task()` now returns a list of task dictionaries instead of a single one.
- Updated logic for cleaner user input handling (default “no” when pressing Enter).

### Fixed
- Fixed minor bugs when editing tasks without due dates.
- Improved handling of invalid date inputs in `edit_task`.
- Fixed `break` behavior in date validation to use `continue` instead.
- Prevented blank task entries from being added.
- Improved validation flow and feedback for user commands.

---

## [v1.0] - 2025-10-06

### Added
- Initial version of the **To-Do List CLI App**.
- Core features:
  - Add single task  
  - View all tasks  
  - Mark tasks as completed  
  - Delete tasks  
  - Save and load tasks using JSON

---

