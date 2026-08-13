from core.messages import Message
from core.tools import TOOLS


def fake_model(messages):
    """Pretend to be a model that decides the next agent action.

    Input:
    - messages: the current conversation history.

    Output:
    - A decision dictionary.
    - If the model wants a tool, it returns:
      {"type": "tool_call", "tool": tool_name, "args": {...}}
    - If the model is ready to answer, it returns:
      {"type": "answer", "text": answer_text}
    """

    # Look at the newest message.
    # In a real agent, the model would look at the whole message history.
    latest_message = messages[-1]
    latest = latest_message.content

    # Lowercase makes simple keyword matching easier.
    # Example: "Time" and "time" become the same for this fake model.
    latest_lower = latest.lower()

    # If the newest message is a tool result, the model has already observed
    # the tool output. Now it should produce a final answer instead of calling
    # another tool.
    if latest_message.role == "tool_result":
        return {"type": "answer", "text": f"My answer based on the tool result:\n{latest}"}

    # Only user messages can trigger new tool calls in this simple version.
    # This keeps the loop easy to reason about.
    if latest_message.role == "user":
        # If the user asks about time, the fake model decides to call get_time.
        if "time" in latest_lower:
            return {"type": "tool_call", "tool": "get_time", "args": {}}

        # If the user asks to calculate something, the fake model decides to
        # call calculate.
        if "calculate" in latest_lower:
            # Remove the word "calculate" so only the math expression remains.
            # Example: "calculate 127*83" becomes "127*83".
            expression = latest_lower.replace("calculate", "").strip()
            return {"type": "tool_call", "tool": "calculate", "args": {"expression": expression}}

    # If no tool is needed, or a tool result is already available,
    # the fake model returns a final answer.
    return {"type": "answer", "text": f"My answer based on the current context:\n{latest}"}


def run_agent(user_input, max_steps=5):
    """Run the agent loop for one user request.

    Input:
    - user_input: the user's task or question.
    - max_steps: safety limit to avoid an infinite loop.

    Output:
    - messages: the full conversation history produced during this run.
    """

    # Start the conversation history with the user's first message.
    messages = [Message(role="user", content=user_input)]

    # This is the Agent Loop.
    # It lets the agent think, call tools, observe results, and think again.
    # max_steps prevents the loop from running forever.
    for _step in range(max_steps):
        # Ask the model what to do next.
        # In this first version, fake_model replaces a real LLM.
        decision = fake_model(messages)

        # If the model says it is ready to answer, save the assistant answer
        # and end the agent run.
        if decision["type"] == "answer":
            messages.append(Message(role="assistant", content=decision["text"]))
            return messages

        # If the model asks for a tool, run that tool.
        if decision["type"] == "tool_call":
            # Get the tool name chosen by the model.
            tool_name = decision["tool"]
            tool_args = decision["args"]

            # CHANGED: record the model's tool call as an assistant message.
            # Real agent frameworks keep this step in history:
            # user -> assistant(tool_call) -> tool_result -> assistant(answer).
            # This makes the trace easier to inspect and closer to real tool calling.
            messages.append(Message(role="assistant", content=f"tool_call: {tool_name} args={tool_args}"))

            # Find the Tool object from the tool registry.
            # Example: "get_time" becomes Tool(name="get_time", ...).
            tool = TOOLS[tool_name]

            # Run the tool with the arguments chosen by the model.
            # **decision["args"] means:
            # turn {"expression": "127*83"} into calculate(expression="127*83").
            result = tool.run(**tool_args)

            # Save the raw tool result in the message history.
            messages.append(Message(role="tool_result", content=f"{tool_name}: {result}"))

            # Go back to the top of the loop so the model can think again
            # with the tool result now included in messages.
            continue

    # If we reach this point, the agent used too many steps.
    # Return a safe stop message instead of looping forever.
    messages.append(Message(role="assistant", content="I stopped because there were too many steps."))
    return messages
