from datetime import datetime
from dataclasses import dataclass
from typing import Callable


@dataclass
class Tool:
    """A tool definition that the agent can call.

    Input fields:
    - name: the tool name the model uses, such as "get_time".
    - description: a human-readable explanation of what the tool does.
    - function: the Python function that actually runs.
    - required_args: argument names that must be present before the tool can run.

    Output:
    - A Tool object stored in the tool registry.
    """

    name: str
    description: str
    function: Callable
    required_args: list[str]

    def run(self, **kwargs):
        """Run this tool with keyword arguments.

        Input:
        - kwargs: arguments for the underlying Python function.
        - Example: {"expression": "127*83"}

        Output:
        - Whatever the underlying function returns.
        """

        # Check required arguments before running the tool.
        # This is the first tiny version of "tool argument validation".
        # Later, this will become a real schema system.
        for arg_name in self.required_args:
            # If a required argument is missing, return a clear error message.
            # This keeps the agent from crashing when the model makes a bad tool call.
            if arg_name not in kwargs:
                return f"Error: missing required argument '{arg_name}'."

        # Run the actual Python function only after validation passes.
        return self.function(**kwargs)


def get_time():
    """Return the current local time.

    Input:
    - No input.

    Output:
    - A string like "11:34:26".
    """

    return datetime.now().strftime("%H:%M:%S")


def calculate(expression):
    """Calculate a simple arithmetic expression.

    Input:
    - expression: a string such as "127*83".

    Output:
    - A string containing the calculation result, or an error message.
    """

    # Only allow simple math characters.
    # This prevents dangerous text such as function calls or file operations.
    allowed = set("0123456789+-*/(). ")

    # Check whether every character in the expression is allowed.
    # If not, stop early and return an error instead of running eval().
    if not set(expression) <= allowed:
        return "Error: expression contains unsupported characters."

    # Run the calculation after the safety check above.
    # "__builtins__": {} removes access to Python built-in functions.
    return str(eval(expression, {"__builtins__": {}}, {}))


# Tool registry.
#
# Input:
# - A tool name chosen by the model, such as "get_time".
#
# Output:
# - A Tool object that contains name, description, and the function to run.
TOOLS = {
    "get_time": Tool(
        name="get_time",
        description="Get the current local time.",
        function=get_time,
        required_args=[],
    ),
    "calculate": Tool(
        name="calculate",
        description="Calculate a simple arithmetic expression.",
        function=calculate,
        # calculate requires one argument named "expression".
        # If the model forgets it, Tool.run() will return an error.
        required_args=["expression"],
    ),
}


def list_tools():
    """Return a readable list of tools the agent is allowed to use.

    Input:
    - No input.

    Output:
    - A list of strings.
    - Each string explains one tool's name, required arguments, and description.
    """

    # CHANGED: this helper turns the tool registry into a "tool menu".
    # Real agents put information like this into the model context so the
    # model knows which tools exist and how to call them.
    tool_lines = []

    # Read every Tool object from the registry.
    # tool_name is the dictionary key, such as "calculate".
    # tool is the Tool object that stores description and required arguments.
    for tool_name, tool in TOOLS.items():
        # If the tool has required arguments, show them as comma-separated text.
        # Example: ["expression"] becomes "expression".
        if tool.required_args:
            args_text = ", ".join(tool.required_args)
        else:
            # If the list is empty, this tool can be called with no arguments.
            args_text = "none"

        # Build one readable line for this tool.
        # Example:
        # - calculate(args: expression): Calculate a simple arithmetic expression.
        tool_lines.append(f"- {tool_name}(args: {args_text}): {tool.description}")

    # Give the caller the full tool menu.
    return tool_lines
