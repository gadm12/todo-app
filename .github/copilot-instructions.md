Purpose
This file gives concise, project-specific guidance to AI coding assistants working on this repository so they can be productive immediately.

Big picture

- **Two apps**: a Flask web app in `todo_flask/` (primary, browser UI + OCR schedule parsing) and a CLI tool in `todo_cli/` (simple local JSON-backed to-do list).
- **Data flow**: `todo_flask` stores users, todos and parsed schedules in a local SQLite DB (`sqlite:///tasks.db`). Uploaded schedule images are saved to `uploads/` and parsed into JSON stored on `Schedule.parsed_data`.
- **Why this structure**: the Flask app groups web concerns (routes, templates, static) and domain models (`models.py`). OCR/vision logic is isolated in `parser.py` so it can be iterated independently.

Key files & patterns (use these as anchors when editing)

- `todo_flask/app.py`: app entrypoint and most route handlers. Note: running this file will call `db.create_all()` and start the dev server (`app.run(debug=True)`).
- `todo_flask/models.py`: SQLAlchemy models — `User`, `Todo`, `Schedule`. Dates use UTC in defaults.
- `todo_flask/parser.py`: `ScheduleParser` — OpenCV + EasyOCR based pipeline. Look here for OCR heuristics, debug image dumps (`uploads/modified/debug_thresh.png`) and many regex-based corrections.
- `todo_flask/templates/` and `todo_flask/static/`: front-end markup and CSS. Keep UI changes compatible with server-rendered templates.
- `todo_cli/to_do_list.py`: standalone CLI. Reads/writes `to_do_list.json` in its working directory.

Run / dev workflow (Windows `cmd.exe`)

- Run Flask app (creates DB automatically):

```
python todo_flask/app.py
```

- Run CLI tool:

```
python todo_cli/to_do_list.py
```

- When editing `parser.py`, use the `main()` at bottom to test parsing quickly:

```
python todo_flask/parser.py
```

Project-specific conventions & gotchas

- DB: app uses `sqlite:///tasks.db` configured in `app.py`. Running `app.py` in project root will put `tasks.db` next to that script.
- Auth: passwords are hashed with `flask_bcrypt`. `SECRET_KEY` is hardcoded to `"doors"` in `app.py` — do not replace or rekey automatically in PRs; flag it in review if you plan to change secrets.
- OCR: `ScheduleParser` instantiates EasyOCR with `gpu=False` by default. Loading the reader is slow and printed at app startup — tests and quick runs should mock or skip heavy model loading when possible.
- Uploads: uploaded files are stored under `uploads/`. Parser writes debug artifacts to `uploads/modified/` — these paths are used by code and should be preserved when changing behavior.
- Timezones: ICS export in `app.py` localizes events to `America/Chicago`. If changing time logic, update `export_ics` carefully and add tests for overnight shifts crossing midnight.

Editing guidance for AI agents

- Prefer minimal, targeted edits. Keep route semantics and template variable names stable (e.g., `tasks`, `schedule`, `current_time` used by templates).
- For parser improvements, add a small unit-style script or extend `parser.py`'s `main()` so changes can be validated locally without launching Flask.
- Keep prints and `flash()` usage consistent: server-side user-facing messages use `flash(..., category)`; debugging prints are fine but avoid removing flash flows.

Dependencies to note

- Visible imports used at runtime: `flask`, `flask_sqlalchemy`, `flask_login`, `flask_bcrypt`, `easyocr`, `opencv-python` (`cv2`), `numpy`, `ics`, `pytz`, `werkzeug`.
- There is no central `requirements.txt` in the repo; when adding or testing, install these packages into your environment.

Examples (copyable snippets)

- Create DB & run server (from repo root):

```
python todo_flask/app.py
```

- Quick parser debug (uses `test2.png` placeholder in `parser.py`):

```
python todo_flask/parser.py
```

What to ask the human before committing large changes

- Should the hardcoded `SECRET_KEY` be rotated or moved to environment variables?
- Is backward compatibility required for existing uploaded images and saved `Schedule.parsed_data` JSON shape?

If anything here is incomplete or ambiguous, tell me which area (run, parser, auth, DB, templates) and I'll expand or adjust these instructions.
