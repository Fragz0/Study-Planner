import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# Import functions from our own files
from database import create_table, seed_sample_data, add_task, get_all_tasks, update_task_status, delete_task
from utils import PRIORITIES, STATUSES, validate_task, days_until_due
from ai_features import generate_study_recommendations

# =============================================================================
# PAGE SETUP
# =============================================================================
st.set_page_config(page_title="Study Planner", page_icon="📚", layout="wide")

# Simple CSS — uses transparent backgrounds so it works with both light and dark themes
st.markdown("""
<style>
    /* Metric boxes: subtle border and rounded corners, no colour override */
    div[data-testid="metric-container"] {
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 10px;
        padding: 16px;
    }
    /* Form card: just a rounded border, no colour override */
    div[data-testid="stForm"] {
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 10px;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Priority emoji — shown next to each task in the dashboard
PRIORITY_EMOJI = {
    "Low":      "🟢",
    "Medium":   "🟡",
    "High":     "🟠",
    "Critical": "🔴",
}

# Start the database — wrapped in try/except so errors show a friendly message
try:
    create_table()
    seed_sample_data()
except Exception as e:
    st.error(f"Could not connect to the database: {e}")
    st.stop()

# =============================================================================
# SIDEBAR
# =============================================================================
st.sidebar.title("📚 Study Planner")
st.sidebar.markdown("Track your study tasks in one place.")
st.sidebar.markdown("---")

page = st.sidebar.radio("Go to:", ["📋 Dashboard", "➕ Add Task", "📊 Analytics", "📝 Study Assistant"])

st.sidebar.markdown("---")

# Load summary numbers for the sidebar
all_tasks = get_all_tasks()
total = len(all_tasks)
done  = len(all_tasks[all_tasks["status"] == "Completed"]) if total > 0 else 0

st.sidebar.write(f"**Total tasks:** {total}")
st.sidebar.write(f"**Completed:** {done}")
st.sidebar.write(f"**Remaining:** {total - done}")

# Progress bar so the user can see their completion percentage
if total > 0:
    progress = done / total
    st.sidebar.progress(progress, text=f"{round(progress * 100)}% done")


# =============================================================================
# PAGE 1 — DASHBOARD
# =============================================================================
if page == "📋 Dashboard":

    st.title("📋 My Tasks")
    st.caption("View, filter, and update all your study tasks.")

    df = get_all_tasks()

    if df.empty:
        st.info("No tasks yet. Go to **➕ Add Task** to create one.")

    else:
        # Metrics row at the top
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tasks", total)
        col2.metric("Completed",   done)
        col3.metric("Remaining",   total - done)

        st.divider()

        # Filter controls
        st.subheader("🔍 Filter Tasks")
        col_a, col_b = st.columns(2)
        filter_status = col_a.selectbox("Filter by status:", ["All"] + STATUSES)
        search_text   = col_b.text_input("Search by title:", placeholder="e.g. Chapter 5")

        # Apply filters step by step
        filtered = df.copy()

        if filter_status != "All":
            filtered = filtered[filtered["status"] == filter_status]

        if search_text:
            # str.contains checks whether the search text appears in the title column
            filtered = filtered[filtered["title"].str.contains(search_text, case=False, na=False)]

        st.caption(f"Showing {len(filtered)} task(s)")
        st.divider()

        # Display each task as a row
        for index, row in filtered.iterrows():

            # Calculate how many days until the task is due
            days_left = days_until_due(row["due_date"])

            if days_left is None:
                days_text = "Unknown date"
            elif days_left < 0:
                days_text = f"⚠️ {abs(days_left)} days overdue!"
            elif days_left == 0:
                days_text = "📅 Due today!"
            elif days_left == 1:
                days_text = "⏰ Due tomorrow!"
            else:
                days_text = f"📆 {days_left} days left"

            # Get the coloured emoji for this task's priority level
            p_emoji = PRIORITY_EMOJI.get(row["priority"], "⚪")

            col1, col2, col3, col4 = st.columns([3, 1, 2, 1])

            col1.write(f"**{row['title']}** — {row['subject']}")
            col1.caption(f"{days_text}  |  {p_emoji} {row['priority']}")
            col2.write(row["status"])

            # Dropdown to change the task status inline
            new_status = col3.selectbox(
                "Change status",
                STATUSES,
                index=STATUSES.index(row["status"]),
                key=f"status_{row['id']}",
                label_visibility="collapsed"
            )

            # Save the new status if it changed
            if new_status != row["status"]:
                try:
                    update_task_status(int(row["id"]), new_status)
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not update status: {e}")

            # Delete button
            if col4.button("Delete", key=f"delete_{row['id']}"):
                try:
                    delete_task(int(row["id"]))
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not delete task: {e}")

            # Show notes if this task has any
            if row["notes"]:
                st.caption(f"📝 {row['notes']}")

            st.divider()


# =============================================================================
# PAGE 2 — ADD TASK
# =============================================================================
elif page == "➕ Add Task":

    st.title("➕ Add a New Task")
    st.caption("Fill in the form and click Add Task to save it to the database.")

    with st.form("add_task_form", clear_on_submit=True):

        subject  = st.text_input("Subject",       placeholder="e.g. Mathematics")
        title    = st.text_input("Task Title",     placeholder="e.g. Review Chapter 5")
        due_date = st.date_input("Due Date",       min_value=date.today())

        col1, col2 = st.columns(2)
        priority = col1.selectbox("Priority", PRIORITIES)
        status   = col2.selectbox("Status",   STATUSES)

        notes    = st.text_area("Notes (optional)", placeholder="Any extra details...")

        submitted = st.form_submit_button("➕ Add Task", type="primary")

    # This block runs when the button is clicked
    if submitted:
        errors = validate_task(subject, title, due_date)

        if errors:
            for error in errors:
                st.error(error)
        else:
            try:
                add_task(subject, title, str(due_date), priority, status, notes or None)
                st.success(f"✅ Task '{title}' added successfully!")
            except Exception as e:
                st.error(f"Could not save task: {e}")


# =============================================================================
# PAGE 3 — ANALYTICS
# =============================================================================
elif page == "📊 Analytics":

    st.title("📊 Analytics")
    st.caption("A visual summary of all your tasks.")

    try:
        df = get_all_tasks()
    except Exception as e:
        st.error(f"Could not load tasks: {e}")
        st.stop()

    if df.empty:
        st.info("No tasks yet. Add some tasks to see charts here.")

    else:
        # Chart 1: tasks by status
        st.subheader("Tasks by Status")
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig1 = px.bar(status_counts, x="Status", y="Count", color="Status")
        st.plotly_chart(fig1, use_container_width=True)

        # Chart 2: tasks by priority
        st.subheader("Tasks by Priority")
        priority_counts = df["priority"].value_counts().reset_index()
        priority_counts.columns = ["Priority", "Count"]
        fig2 = px.pie(priority_counts, values="Count", names="Priority")
        st.plotly_chart(fig2, use_container_width=True)

        # Chart 3: tasks by subject
        st.subheader("Tasks by Subject")
        subject_counts = df["subject"].value_counts().reset_index()
        subject_counts.columns = ["Subject", "Count"]
        fig3 = px.bar(subject_counts, x="Subject", y="Count", color="Subject")
        st.plotly_chart(fig3, use_container_width=True)

        # Full data table at the bottom
        st.subheader("All Tasks")
        st.dataframe(df, use_container_width=True, hide_index=True)


# =============================================================================
# PAGE 4 — STUDY ASSISTANT
# =============================================================================
elif page == "📝 Study Assistant":

    st.title("📝 Study Assistant")
    st.caption("The app suggests what to study first based on your priorities, deadlines, and task status. No API key needed.")

    try:
        df = get_all_tasks()
    except Exception as e:
        st.error(f"Could not load tasks: {e}")
        st.stop()

    if df.empty:
        st.info("Add some tasks first so the assistant has something to work with.")

    else:
        active_count = len(df[df["status"] != "Completed"])
        st.write(f"You have **{active_count}** active task(s). Click the button to get suggestions.")

        if st.button("📋 Get Study Recommendations", type="primary"):

            with st.spinner("Analysing your tasks..."):
                try:
                    result, error = generate_study_recommendations(df)
                except Exception as e:
                    result = None
                    error = str(e)

            if error:
                st.error(f"Something went wrong: {error}")
            else:
                st.success("Here is your study plan for today:")
                st.markdown(result)
