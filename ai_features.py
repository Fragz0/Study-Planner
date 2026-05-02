from datetime import datetime, date


def generate_study_recommendations(tasks_df):
    """
    Generate study recommendations based on the task data.
    No API key needed — this uses simple Python rules.
    """

    today = date.today()

    # Split tasks into active and completed
    active_tasks = tasks_df[tasks_df["status"] != "Completed"]
    completed_count = len(tasks_df[tasks_df["status"] == "Completed"])

    if active_tasks.empty:
        return "Great job! You have no active tasks right now. 🎉", None

    # Go through each active task and sort them into groups
    overdue    = []  # tasks where the due date has already passed
    due_soon   = []  # tasks due in the next 3 days
    high_prio  = []  # tasks marked High or Critical

    for index, row in active_tasks.iterrows():

        # Calculate how many days until the due date
        try:
            due = datetime.strptime(str(row["due_date"]), "%Y-%m-%d").date()
            days_left = (due - today).days
        except Exception:
            days_left = 99  # if we can't read the date, skip it

        if days_left < 0:
            overdue.append({
                "title":   row["title"],
                "subject": row["subject"],
                "days":    abs(days_left)
            })
        elif days_left <= 3:
            due_soon.append({
                "title":   row["title"],
                "subject": row["subject"],
                "days":    days_left
            })

        if row["priority"] in ["High", "Critical"]:
            high_prio.append({
                "title":    row["title"],
                "subject":  row["subject"],
                "priority": row["priority"]
            })

    # ── Build the recommendation text ────────────────────────────────────────
    lines = []

    # Section 1 — what to work on today
    lines.append("**Today's Focus**")

    urgent = overdue + due_soon  # overdue tasks are most urgent

    if urgent:
        # Show the top 3 most urgent tasks
        for task in urgent[:3]:
            if task in overdue:
                lines.append(f"- **{task['subject']}: {task['title']}** — {task['days']} day(s) overdue, do this first!")
            else:
                lines.append(f"- **{task['subject']}: {task['title']}** — due in {task['days']} day(s)")

    elif high_prio:
        # No urgent deadlines, so focus on high-priority tasks
        for task in high_prio[:3]:
            lines.append(f"- **{task['subject']}: {task['title']}** ({task['priority']} priority)")

    else:
        # No urgent tasks — just show the first few from the list
        for i, (index, row) in enumerate(active_tasks.iterrows()):
            if i >= 3:
                break
            lines.append(f"- {row['subject']}: {row['title']}")

    # Section 2 — study tips
    lines.append("")
    lines.append("**Study Tips**")

    total_active = len(active_tasks)

    if total_active > 5:
        lines.append("- You have many tasks — break each one into 25-minute focused sessions (Pomodoro technique)")
    else:
        lines.append("- Tackle your hardest task first while your energy is highest")

    if overdue:
        lines.append(f"- You have {len(overdue)} overdue task(s) — clear these before starting anything new")
    else:
        lines.append("- Review your notes from the previous session before starting a new topic")

    # Section 3 — warnings (only if there are overdue tasks)
    if overdue:
        lines.append("")
        lines.append("**Watch Out**")
        for task in overdue:
            lines.append(f"- ⚠️ {task['subject']}: {task['title']} is {task['days']} day(s) overdue")

    # Section 4 — encouragement
    lines.append("")
    lines.append("**Keep Going**")

    if completed_count > 0:
        lines.append(f"- You have already completed {completed_count} task(s) — great progress, keep it up!")
    else:
        lines.append("- Every big goal starts with a single task. You've got this!")

    # Join all lines into one string and return it
    result = "\n".join(lines)
    return result, None
