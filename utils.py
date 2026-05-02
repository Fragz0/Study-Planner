from datetime import datetime, date

# These lists are used to fill the dropdowns in the app
PRIORITIES = ["Low", "Medium", "High", "Critical"]
STATUSES   = ["Not Started", "In Progress", "Completed", "On Hold"]


def validate_task(subject, title, due_date):
    """
    Check that the task form inputs are valid.
    Returns a list of error strings (empty list means no errors).
    """
    errors = []

    if not subject or not subject.strip():
        errors.append("Subject cannot be empty.")

    if not title or not title.strip():
        errors.append("Title cannot be empty.")

    if due_date is None:
        errors.append("Due date is required.")

    return errors


def days_until_due(due_date_str):
    """
    Work out how many days remain until the due date.
    Returns a number — negative means the task is overdue.
    Returns None if the date string is invalid.
    """
    try:
        due = datetime.strptime(str(due_date_str), "%Y-%m-%d").date()
        days_left = (due - date.today()).days
        return days_left
    except Exception:
        return None
