import os
import anthropic


def generate_study_recommendations(tasks_df):
    """
    Send the student's tasks to Claude AI and get back study recommendations.
    Returns (result_text, error_message).
    One of them will be None depending on whether it worked.
    """

    # Read the API key from the environment
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        error = "ANTHROPIC_API_KEY is not set. Add it to your environment to use AI features."
        return None, error

    # Create the Anthropic client with the key
    client = anthropic.Anthropic(api_key=api_key)

    # Build a plain-text list of the active tasks to send to Claude
    task_lines = ""
    for index, row in tasks_df.iterrows():
        if row["status"] != "Completed":
            task_lines += f"- {row['subject']}: {row['title']}  (Priority: {row['priority']}, Due: {row['due_date']}, Status: {row['status']})\n"

    if task_lines == "":
        task_lines = "No active tasks."

    # Write the prompt — this is the message Claude will receive
    prompt = f"""You are a helpful and friendly study coach.

Here are the student's current tasks:
{task_lines}

Please give them:
1. The top 2-3 tasks to focus on today and why
2. Two short study tips for managing this workload
3. One encouraging sentence to keep them motivated

Keep the response short, friendly, and easy to read."""

    # Call the Claude API and return the response text
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        result_text = response.content[0].text
        return result_text, None

    except Exception as e:
        return None, f"AI error: {str(e)}"
