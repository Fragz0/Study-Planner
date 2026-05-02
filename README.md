# Study Planner

A simple Streamlit web app that helps students manage their study tasks, track progress, view analytics, and get study suggestions.

**No API key required. No paid services. Works offline.**

---

## What the app does

- **Dashboard** — see all your tasks, filter by status, search by title, update status, delete tasks
- **Add Task** — add a new task with subject, title, due date, priority, status, and notes
- **Analytics** — three charts showing your tasks by status, priority, and subject
- **Study Assistant** — suggests what to study based on your priorities, deadlines, and overdue tasks

---

## How to run it

**Step 1 — Install the required packages**

```
pip install -r requirements.txt
```

**Step 2 — Start the app**

```
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.
Sample tasks are added automatically the first time you run it.

---

## Project files

```
app.py          — the main Streamlit app (all four pages)
database.py     — functions for saving and loading tasks (SQLite)
utils.py        — helper functions and constants used across the app
ai_features.py  — the study assistant logic (rule-based, no API needed)
requirements.txt
```

---

## Database

The app uses SQLite. The database file (`study_tasks.db`) is created automatically when you first run the app.

| Column   | What it stores                                          |
|----------|---------------------------------------------------------|
| id       | Unique number for each task (added automatically)       |
| subject  | The subject, e.g. Mathematics                           |
| title    | The task description, e.g. Review Chapter 5             |
| due_date | The date the task is due (YYYY-MM-DD)                   |
| priority | Low, Medium, High, or Critical                          |
| status   | Not Started, In Progress, Completed, or On Hold         |
| notes    | Any extra notes (optional)                              |

---

## Study Assistant (how it works)

The Study Assistant does **not** use any AI API or paid service.
It uses simple Python rules to look at your tasks and suggest what to focus on:

1. If you have **overdue tasks** — it tells you to do those first
2. If you have tasks **due in the next 3 days** — it highlights them
3. If you have **High or Critical priority** tasks — it recommends those
4. It also gives a short study tip and an encouraging message

---

## Technologies used

- [Streamlit](https://streamlit.io) — the web app framework
- [SQLite](https://www.sqlite.org) — the database (built into Python, no setup needed)
- [Pandas](https://pandas.pydata.org) — for reading and filtering task data
- [Plotly](https://plotly.com/python) — for the charts on the Analytics page
