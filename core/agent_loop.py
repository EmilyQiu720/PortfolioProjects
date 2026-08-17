from core.model import choose_next_action
from core.session import AgentSession
from core.tools import TOOLS, ToolResult


def execute_tool_call(tool_name, tool_args):
    """Find and run a tool requested by the model.

    Input:
    - tool_name: the name of the tool the model wants to call.
    - tool_args: a dictionary of arguments for that tool.

    Output:
    - A ToolResult containing either the tool output or a clear error message.
    """

    # This keeps run_agent() focused on the loop, while this function handles
    # tool lookup, unknown-tool errors, and actual execution.

    # Check whether the requested tool exists in the registry.
    # This protects the agent from crashing if the model invents a tool name.
    if tool_name not in TOOLS:
        return ToolResult(
            ok=False,
            content="",
            error=f"Error: unknown tool '{tool_name}'.",
        )

    # Find the Tool object from the tool registry.
    # Example: "get_time" becomes Tool(name="get_time", ...).
    tool = TOOLS[tool_name]

    # Run the tool with the arguments chosen by the model.
    # **tool_args means:
    # turn {"expression": "127*83"} into calculate(expression="127*83").
    return tool.run(**tool_args)


def run_agent_session(user_input, max_steps=5):
    """Run the agent loop and return the full AgentSession.

    Input:
    - user_input: the user's task or question.
    - max_steps: safety limit to avoid an infinite loop.

    Output:
    - An AgentSession containing metadata and the full message history.
    """

    # Session owns messages plus run metadata like id and step count.
    # This is the first version of "agent state/session" in the project.
    session = AgentSession.create(user_input)

    # This is the Agent Loop.
    # It lets the agent think, call tools, observe results, and think again.
    # max_steps prevents the loop from running forever.
    for _step in range(max_steps):
        # Ask the model what to do next.
        # In this first version, choose_next_action() replaces a real LLM.
        decision = choose_next_action(session.messages)

        # Record that the model made one decision in this session.
        session.mark_step_finished()

        # If the model says it is ready to answer, save the assistant answer
        # and end the agent run.
        if decision["type"] == "answer":
            session.add_message(role="assistant", content=decision["text"])
            return session

        # If the model asks for a tool, run that tool.
        if decision["type"] == "tool_call":
            # Get the tool name chosen by the model.
            tool_name = decision["tool"]
            tool_args = decision["args"]

            # Real agent frameworks keep this step in history:
            # user -> assistant(tool_call) -> tool_result -> assistant(answer).
            # This makes the trace easier to inspect and closer to real tool calling.
            session.add_message(role="assistant", content=f"tool_call: {tool_name} args={tool_args}")

            # Ask the tool execution helper to find and run the tool.
            # If the tool name is unknown, this returns ToolResult(ok=False).
            result = execute_tool_call(tool_name, tool_args)

            # Convert the structured ToolResult back into text for the message trace.
            result_text = result.to_message_text()

            # Save the tool result in the message history.
            session.add_message(role="tool_result", content=f"{tool_name}: {result_text}")

            # Go back to the top of the loop so the model can think again
            # with the tool result now included in messages.
            continue

    # If we reach this point, the agent used too many steps.
    # Return a safe stop message instead of looping forever.
    session.add_message(role="assistant", content="I stopped because there were too many steps.")
    return session


def run_agent(user_input, max_steps=5):
    """Run the agent loop and return only the message history.

    Input:
    - user_input: the user's task or question.
    - max_steps: safety limit to avoid an infinite loop.

    Output:
    - messages: the full conversation history produced during this run.
    """

    # Run the richer session function first.
    # This wrapper keeps the old CLI behavior simple: it still receives messages.
    session = run_agent_session(user_input=user_input, max_steps=max_steps)

    # Return only messages for callers that do not care about metadata yet.
    return session.messages
