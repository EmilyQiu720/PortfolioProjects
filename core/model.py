def choose_next_action(messages):
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

    # Model decision logic now lives in its own model layer.
    # Later, this is where we can replace fake keyword logic with a real LLM call.

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

        # This branch exists only for learning and testing.
        # It lets us see what happens when the model asks for a tool that does not exist.
        if "unknown tool" in latest_lower:
            return {"type": "tool_call", "tool": "missing_tool", "args": {}}

    # If no tool is needed, or a tool result is already available,
    # the fake model returns a final answer.
    return {"type": "answer", "text": f"My answer based on the current context:\n{latest}"}
