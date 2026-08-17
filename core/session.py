from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from core.context import build_initial_messages
from core.messages import Message


@dataclass
class AgentSession:
    """One run of the agent, including metadata and messages.

    Input fields:
    - user_input: the original user request.
    - session_id: a unique id for this run.
    - created_at: when this session was created.
    - messages: the conversation history for this run.
    - step_count: how many loop steps have happened.

    Output:
    - An AgentSession object used by the agent loop.
    """

    user_input: str
    session_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    messages: list[Message] = field(default_factory=list)
    step_count: int = 0

    @classmethod
    def create(cls, user_input):
        """Create a new session from a user request.

        Input:
        - user_input: the user's question or task.

        Output:
        - An AgentSession with initial system and user messages already loaded.
        """

        # Session creation owns the initial message setup.
        # This keeps run_agent() focused on running the loop, not preparing state.

        # Create a session object with id, timestamp, and empty messages.
        session = cls(user_input=user_input)

        # Build system + user messages through the context builder.
        session.messages = build_initial_messages(user_input)

        # Return the ready-to-run session.
        return session

    def add_message(self, role, content):
        """Append one message to this session's history.

        Input:
        - role: who produced the message, such as "assistant" or "tool_result".
        - content: the text stored in the message.

        Output:
        - The newly created Message object.
        """

        # Create the Message object first so it has the same shape everywhere.
        message = Message(role=role, content=content)

        # Store the message in this session's conversation history.
        self.messages.append(message)

        # Return the message in case another caller wants to inspect it.
        return message

    def mark_step_finished(self):
        """Record that one agent loop step has completed.

        Input:
        - No input.

        Output:
        - The updated step count as an integer.
        """

        # Add one because the agent just completed one loop iteration.
        self.step_count += 1

        # Return the number so logs/tests can inspect it later.
        return self.step_count
