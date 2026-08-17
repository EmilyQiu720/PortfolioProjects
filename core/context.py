from core.messages import Message
from core.tools import list_tools


def build_system_prompt():
    """Build the instruction message that tells the agent what it can do.

    Input:
    - No input.

    Output:
    - A string that will become the system message content.
    """

    # Context construction means: collect useful information before the model thinks.

    # Ask the tool registry for a readable list of available tools.
    # Example output line:
    # - calculate(args: expression): Calculate a simple arithmetic expression.
    tool_lines = list_tools()

    # Join the tool lines into one text block.
    # "\n" means "new line", so each tool stays on its own line.
    tools_text = "\n".join(tool_lines)

    # Build the system prompt.
    # A system prompt is higher-level instruction/context for the model.
    return (
        "You are a learning agent.\n"
        "You can answer directly, or call one of these tools when useful:\n"
        f"{tools_text}"
    )


def build_initial_messages(user_input):
    """Create the first messages for one agent run.

    Input:
    - user_input: the question or task typed by the user.

    Output:
    - A list of Message objects.
    - The list starts with system context, then the user message.
    """

    # Build the system prompt first, because the model should see instructions
    # and available tools before it sees the user's task.
    system_prompt = build_system_prompt()

    # Return the first conversation history.
    # The order matters:
    # 1. system: rules and tool menu
    # 2. user: the actual request
    return [
        Message(role="system", content=system_prompt),
        Message(role="user", content=user_input),
    ]
