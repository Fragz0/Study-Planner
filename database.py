import sqlite3
import pandas as pd

DATABASE_NAME = "study_tasks.db"


def get_connection():
    # Open a connection to the SQLite database file
    conn = sqlite3.connect(DATABASE_NAME)
    return conn


def create_table():
    # Create the tasks table if it does not already exist
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                subject  TEXT NOT NULL,
                title    TEXT NOT NULL,
                due_date TEXT NOT NULL,
                priority TEXT NOT NULL,
                status   TEXT NOT NULL,
                notes    TEXT
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        conn.close()  # always close the connection, even if an error happened


def add_task(subject, title, due_date, priority, status, notes):
    # Insert one new task row into the database
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (subject, title, due_date, priority, status, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (subject, title, due_date, priority, status, notes))
        conn.commit()
    except Exception as e:
        print(f"Error adding task: {e}")
    finally:
        conn.close()


def get_all_tasks():
    # Read every task from the database and return it as a pandas DataFrame
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM tasks", conn)
        return df
    except Exception as e:
        print(f"Error reading tasks: {e}")
        return pd.DataFrame()  # return an empty table if something goes wrong
    finally:
        conn.close()


def update_task_status(task_id, new_status):
    # Change the status column for a single task (found by its id)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks
            SET status = ?
            WHERE id = ?
        """, (new_status, task_id))
        conn.commit()
    except Exception as e:
        print(f"Error updating status: {e}")
    finally:
        conn.close()


def update_task(task_id, subject, title, due_date, priority, status, notes):
    # Update every field of a task (used for editing)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks
            SET subject = ?, title = ?, due_date = ?, priority = ?, status = ?, notes = ?
            WHERE id = ?
        """, (subject, title, due_date, priority, status, notes, task_id))
        conn.commit()
    except Exception as e:
        print(f"Error updating task: {e}")
    finally:
        conn.close()


def delete_task(task_id):
    # Remove a task from the database permanently
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting task: {e}")
    finally:
        conn.close()


def seed_sample_data():
    # Add demo tasks when the database is empty (first run only)
    try:
        df = get_all_tasks()
        if not df.empty:
            return  # data already exists, do not add duplicates

        from datetime import date, timedelta
        today = date.today()

        sample_tasks = [
            ("Mathematics",      "Calculus Problem Set 4",   str(today + timedelta(days=2)),  "High",     "In Progress", "Focus on integration by parts"),
            ("Computer Science", "Binary Trees Assignment",   str(today - timedelta(days=1)),  "Critical", "Not Started", "Overdue!"),
            ("Physics",          "Chapter 7 Review",         str(today + timedelta(days=5)),  "Medium",   "Not Started", None),
            ("History",          "Essay Draft: WWII Causes", str(today + timedelta(days=7)),  "Medium",   "In Progress", "Need to cite sources"),
            ("Mathematics",      "Statistics Quiz Prep",     str(today + timedelta(days=3)),  "High",     "Not Started", None),
            ("Literature",       "Poetry Analysis Essay",    str(today + timedelta(days=14)), "Low",      "Completed",   None),
        ]

        for task in sample_tasks:
            add_task(*task)  # * unpacks the tuple into separate arguments

    except Exception as e:
        print(f"Error seeding data: {e}")
