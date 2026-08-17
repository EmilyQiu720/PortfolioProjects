import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Add the project root to Python's import path.
# This lets app/cli.py import files from the core/ folder.
sys.path.insert(0, str(PROJECT_ROOT))

from core.agent_loop import run_agent, run_agent_session
from core.messages import show_messages
from core.tools import list_tools


def main():
    """Run the command-line demo.

    Input:
    - Command-line text after app/cli.py.
    - Example: python app/cli.py "calculate 127*83"

    Output:
    - Nothing is returned. The function prints the agent messages.
    """

    # "--tools" is a tiny learning command that prints the tool menu.
    # This helps us see what a real model would be shown before choosing tools.
    if len(sys.argv) > 1 and sys.argv[1] == "--tools":
        # Ask the tool registry to describe every available tool.
        tool_lines = list_tools()

        # Print each tool description on its own line.
        # The CLI does not return anything; it only displays text for humans.
        for line in tool_lines:
            print(line)

        # Stop here because "--tools" is only inspection, not an agent run.
        return

    # "--debug-session" shows the session object concept in the terminal.
    # This is useful for learning because session metadata is normally hidden inside code.
    if len(sys.argv) > 1 and sys.argv[1] == "--debug-session":
        # Everything after "--debug-session" is treated as the user's actual prompt.
        user_input = " ".join(sys.argv[2:]) or "what time is it?"

        # Run the richer session version so we can inspect metadata.
        session = run_agent_session(user_input)

        # Print the same message trace as the normal CLI.
        show_messages(session.messages)

        # Print session metadata after the trace.
        print(f"session_id: {session.session_id}")
        print(f"created_at: {session.created_at}")
        print(f"step_count: {session.step_count}")

        # Stop here because the debug command already ran the agent.
        return

    # Read the user's text from the command line.
    # Example:
    # python app/cli.py "calculate 127*83"
    #
    # sys.argv[1:] means "everything after app/cli.py".
    # If the user gives no text, use a default question.
    user_input = " ".join(sys.argv[1:]) or "what time is it?"

    # Run the agent loop and get the full message history back.
    messages = run_agent(user_input)

    # Print the full trace so we can learn what happened step by step.
    show_messages(messages)


# This means: only run main() when this file is executed directly.
# If another file imports cli.py, main() will not run automatically.
if __name__ == "__main__":
    main()
