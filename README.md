# Study Planner

A Streamlit web app for planning and tracking study tasks, with AI-powered recommendations and data science analytics.

## What it does

- **Dashboard** — view all tasks, filter by status, search by title, update status inline, delete tasks
- **Add Task** — form with validation to create new study tasks
- **Analytics** — three charts: tasks by status, tasks by priority, tasks by subject
- **AI Assistant** — click a button to get a personalised study plan from Claude AI

## Project structure

```
app.py          — Streamlit UI (all four pages)
database.py     — SQLite data access (CRUD functions)
utils.py        — constants and helper functions
ai_features.py  — Claude AI integration
requirements.txt
```

## Setup

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

**2. (Optional) Enable the AI feature**

Get a free API key from [console.anthropic.com](https://console.anthropic.com), then set it before running:

```bash
# macOS / Linux
export ANTHROPIC_API_KEY=sk-ant-...

# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

**3. Run**

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`. Sample data loads automatically on first run.

## Database

SQLite file (`study_tasks.db`) created automatically. Schema:

| Column   | Type    | Notes                                           |
|----------|---------|-------------------------------------------------|
| id       | INTEGER | Primary key, auto-increment                     |
| subject  | TEXT    | e.g. "Mathematics"                              |
| title    | TEXT    | Task description                                |
| due_date | TEXT    | YYYY-MM-DD                                      |
| priority | TEXT    | Low / Medium / High / Critical                  |
| status   | TEXT    | Not Started / In Progress / Completed / On Hold |
| notes    | TEXT    | Optional                                        |

## AI bonus

The **AI Assistant** page uses Claude Haiku (`claude-haiku-4-5-20251001`) via the Anthropic Python SDK. It reads all active tasks, formats them as a plain-text list, and sends them to Claude with a prompt asking for today's focus, study tips, and encouragement. The response is shown in the app.

## Data science bonus

The **Analytics** page shows three Plotly charts that summarise the task data:
1. Bar chart — task count by status
2. Pie chart — task count by priority
3. Bar chart — task count by subject

These give the user a visual overview of their workload at a glance.

## What I built without AI

- All functions in `database.py` (SQL schema, CRUD operations, seed function)
- Input validation logic in `utils.py` (`validate_task`, `days_until_due`)
- The Dashboard filter and search logic in `app.py`
- The for-loop that renders each task row with columns and buttons
- Wiring the form submission to save and show errors

## AI tools used

| Tool | What I used it for |
|------|--------------------|
| Claude Code | Writing the initial code structure and chart code |
| Claude Haiku (in the app) | Generating live study recommendations |

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. Set `ANTHROPIC_API_KEY` in the app's **Secrets** settings
4. Main file: `app.py`
