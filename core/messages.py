from dataclasses import dataclass


@dataclass
class Message:
    """One item in the agent conversation history.

    Input fields:
    - role: who produced the message, such as "user", "assistant", or "tool_result".
    - content: the text content of the message.

    Output:
    - A Message object that can be stored in the messages list.
    """

    role: str
    content: str


def show_messages(messages):
    """Print all messages in order.

    Input:
    - messages: a list of Message objects.

    Output:
    - Nothing is returned. The function prints messages to the terminal.
    """

    # Go through the message list from first to last.
    for message in messages:
        # Print each message as "role: content" so we can see the agent trace.
        print(f"{message.role}: {message.content}")
