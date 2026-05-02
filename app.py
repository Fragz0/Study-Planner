import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# Import functions from our own files
from database import create_table, seed_sample_data, add_task, get_all_tasks, update_task_status, delete_task
from utils import PRIORITIES, STATUSES, validate_task, days_until_due
from ai_features import generate_study_recommendations

# ── Page setup ────────────────────────────────────────────────────────────────
# This must be the very first Streamlit command in the file
st.set_page_config(page_title="Study Planner", page_icon="📚", layout="wide")

# Create the database table on startup (safe to run every time — won't duplicate)
create_table()
seed_sample_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("📚 Study Planner")

# Radio buttons let the user pick which page to show
page = st.sidebar.radio("Go to:", ["📋 Dashboard", "➕ Add Task", "📊 Analytics", "🤖 AI Assistant"])

# Show a quick summary count in the sidebar
all_tasks = get_all_tasks()
total = len(all_tasks)
done = len(all_tasks[all_tasks["status"] == "Completed"]) if total > 0 else 0

st.sidebar.write(f"Total tasks: {total}")
st.sidebar.write(f"Completed:   {done}")
st.sidebar.write(f"Remaining:   {total - done}")


# =============================================================================
# PAGE 1 — DASHBOARD
# =============================================================================
if page == "📋 Dashboard":

    st.title("📋 My Tasks")

    # Load all tasks from the database
    df = get_all_tasks()

    # If the table is empty, just show a friendly message
    if df.empty:
        st.info("No tasks yet. Go to Add Task to create one.")

    else:
        # Show three key numbers at the top of the page
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tasks", total)
        col2.metric("Completed",   done)
        col3.metric("Remaining",   total - done)

        st.divider()

        # Filters
        st.subheader("Filter Tasks")

        filter_status = st.selectbox("Show status:", ["All"] + STATUSES)
        search_text = st.text_input("Search by title:", placeholder="e.g. Chapter 5")

        # Apply the filters step by step
        filtered = df.copy()  # start with all rows

        if filter_status != "All":
            filtered = filtered[filtered["status"] == filter_status]

        if search_text:
            # str.contains checks whether the search text appears inside the title
            filtered = filtered[filtered["title"].str.contains(search_text, case=False, na=False)]

        st.write(f"Showing {len(filtered)} task(s)")
        st.divider()

        # Loop through each row and display it
        for index, row in filtered.iterrows():

            # Work out how many days until the task is due
            days_left = days_until_due(row["due_date"])

            # Turn the number into a readable label
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

            # Split each task row into four columns
            col1, col2, col3, col4 = st.columns([3, 1, 2, 1])

            col1.write(f"**{row['title']}** — {row['subject']}")
            col1.caption(f"{days_text}  |  Priority: {row['priority']}")
            col2.write(row["status"])

            # Dropdown so the user can change the status directly in the list
            new_status = col3.selectbox(
                "Change status",
                STATUSES,
                index=STATUSES.index(row["status"]),
                key=f"status_{row['id']}",    # each widget needs a unique key
                label_visibility="collapsed"
            )

            # If the user picked a different status, save it to the database
            if new_status != row["status"]:
                update_task_status(int(row["id"]), new_status)
                st.rerun()  # refresh the page so the change shows immediately

            # Delete button
            if col4.button("Delete", key=f"delete_{row['id']}"):
                delete_task(int(row["id"]))
                st.rerun()

            # Show notes below the task if there are any
            if row["notes"]:
                st.caption(f"📝 {row['notes']}")

            st.divider()


# =============================================================================
# PAGE 2 — ADD TASK
# =============================================================================
elif page == "➕ Add Task":

    st.title("➕ Add a New Task")

    # st.form groups all inputs together and submits them at once
    with st.form("add_task_form", clear_on_submit=True):

        subject  = st.text_input("Subject",       placeholder="e.g. Mathematics")
        title    = st.text_input("Task Title",    placeholder="e.g. Review Chapter 5")
        due_date = st.date_input("Due Date",      min_value=date.today())
        priority = st.selectbox("Priority",       PRIORITIES)
        status   = st.selectbox("Status",         STATUSES)
        notes    = st.text_area("Notes (optional)")

        submitted = st.form_submit_button("Add Task", type="primary")

    # This block runs when the user clicks "Add Task"
    if submitted:
        errors = validate_task(subject, title, due_date)

        if errors:
            # Show each validation error as a red box
            for error in errors:
                st.error(error)
        else:
            # Save the new task to the database
            add_task(subject, title, str(due_date), priority, status, notes or None)
            st.success(f"Task '{title}' added!")


# =============================================================================
# PAGE 3 — ANALYTICS
# =============================================================================
elif page == "📊 Analytics":

    st.title("📊 Analytics")

    df = get_all_tasks()

    if df.empty:
        st.info("No tasks yet. Add some tasks to see charts here.")

    else:
        # Chart 1: how many tasks have each status?
        st.subheader("Tasks by Status")

        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]

        fig1 = px.bar(status_counts, x="Status", y="Count", color="Status")
        st.plotly_chart(fig1, use_container_width=True)

        # Chart 2: how many tasks have each priority? (pie chart)
        st.subheader("Tasks by Priority")

        priority_counts = df["priority"].value_counts().reset_index()
        priority_counts.columns = ["Priority", "Count"]

        fig2 = px.pie(priority_counts, values="Count", names="Priority")
        st.plotly_chart(fig2, use_container_width=True)

        # Chart 3: how many tasks per subject?
        st.subheader("Tasks by Subject")

        subject_counts = df["subject"].value_counts().reset_index()
        subject_counts.columns = ["Subject", "Count"]

        fig3 = px.bar(subject_counts, x="Subject", y="Count", color="Subject")
        st.plotly_chart(fig3, use_container_width=True)

        # Show the full data table at the bottom
        st.subheader("All Tasks")
        st.dataframe(df, use_container_width=True, hide_index=True)


# =============================================================================
# PAGE 4 — AI ASSISTANT
# =============================================================================
elif page == "🤖 AI Assistant":

    st.title("🤖 AI Study Assistant")
    st.write("Click the button below to get personalised study recommendations from Claude AI.")

    df = get_all_tasks()

    if df.empty:
        st.info("Add some tasks first so the AI has something to analyse.")

    else:
        active_count = len(df[df["status"] != "Completed"])
        st.write(f"You have {active_count} active task(s). The AI will read them and suggest a study plan.")

        if st.button("Get Study Recommendations", type="primary"):

            # Show a spinner while we wait for the API response
            with st.spinner("Asking Claude AI..."):
                result, error = generate_study_recommendations(df)

            if error:
                st.error(error)
                if "ANTHROPIC_API_KEY" in error:
                    st.info("Set the ANTHROPIC_API_KEY environment variable before running the app.")
            else:
                st.markdown(result)
