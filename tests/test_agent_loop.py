import unittest

from core.agent_loop import execute_tool_call, run_agent, run_agent_session


def message_contents(messages):
    """Return only the text content from a list of messages.

    Input:
    - messages: a list of Message objects.

    Output:
    - A list of strings, one string per message.
    """

    # CHANGED: tests use this helper so each test can focus on behavior.
    # Without this helper, every test would repeat the same list-comprehension code.
    return [message.content for message in messages]


class AgentLoopTests(unittest.TestCase):
    """Tests for the current learning agent loop.

    Input:
    - unittest calls each test method automatically.

    Output:
    - Passing tests mean the current agent behavior still works.
    """

    def test_direct_answer_without_tool(self):
        """Check that a normal question gets a direct assistant answer.

        Input:
        - A user prompt that does not ask for any known tool.

        Output:
        - The final message should be an assistant answer.
        """

        # Run the agent with a prompt that should not trigger tool calling.
        messages = run_agent("hello agent")

        # The last message should come from the assistant.
        self.assertEqual(messages[-1].role, "assistant")

        # The answer should mention the original user text.
        self.assertIn("hello agent", messages[-1].content)

    def test_calculate_tool_success(self):
        """Check that calculate prompts call the calculate tool.

        Input:
        - A user prompt containing "calculate 127*83".

        Output:
        - The trace should include a calculate tool call and result 10541.
        """

        # Run the agent with a calculation request.
        messages = run_agent("calculate 127*83")

        # Convert Message objects into plain strings for easier assertions.
        contents = message_contents(messages)

        # Check that the assistant recorded the tool call.
        self.assertIn("tool_call: calculate args={'expression': '127*83'}", contents)

        # Check that the tool result was added back into history.
        self.assertIn("calculate: 10541", contents)

    def test_calculate_tool_error(self):
        """Check that unsafe calculate input returns a readable error.

        Input:
        - A user prompt containing unsupported math characters.

        Output:
        - The trace should include a tool_result error instead of crashing.
        """

        # Run the agent with bad calculator input.
        messages = run_agent("calculate abc")

        # Convert messages to text so the assertion is easy to read.
        contents = message_contents(messages)

        # The calculator should reject letters because only math characters are allowed.
        self.assertIn("calculate: Error: expression contains unsupported characters.", contents)

    def test_unknown_tool_error(self):
        """Check that invented tool names do not crash the agent.

        Input:
        - A user prompt that makes the fake model request a missing tool.

        Output:
        - The tool execution layer should return a structured error message.
        """

        # Run the agent path that intentionally asks for a missing tool.
        messages = run_agent("unknown tool")

        # Convert messages to text so the assertion reads like the terminal trace.
        contents = message_contents(messages)

        # The agent should report the unknown tool instead of raising a Python exception.
        self.assertIn("missing_tool: Error: unknown tool 'missing_tool'.", contents)

    def test_execute_tool_call_returns_structured_error(self):
        """Check execute_tool_call directly for unknown tools.

        Input:
        - A tool name that does not exist in the registry.

        Output:
        - A ToolResult with ok=False and a helpful error string.
        """

        # Call the tool execution helper directly, bypassing the full agent loop.
        result = execute_tool_call("missing_tool", {})

        # Unknown tools should be marked as failed.
        self.assertFalse(result.ok)

        # The error message should name the missing tool.
        self.assertEqual(result.error, "Error: unknown tool 'missing_tool'.")

    def test_session_metadata_is_recorded(self):
        """Check that a session stores metadata and messages.

        Input:
        - A normal calculation prompt.

        Output:
        - The session should contain id, timestamp, messages, and step count.
        """

        # Run the richer API that returns the full AgentSession object.
        session = run_agent_session("calculate 2+3")

        # A session id should exist so later logs can identify this run.
        self.assertTrue(session.session_id)

        # created_at should exist so later logs know when the run happened.
        self.assertTrue(session.created_at)

        # The model should make two decisions:
        # 1. call the calculator
        # 2. answer after observing the tool result
        self.assertEqual(session.step_count, 2)

        # The session should store the full message trace.
        self.assertGreaterEqual(len(session.messages), 5)


if __name__ == "__main__":
    unittest.main()
