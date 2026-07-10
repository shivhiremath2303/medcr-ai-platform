from collections import deque
from app.domain.repositories.conversation_repository import ConversationRepository


class MemoryConversationRepository(ConversationRepository):
    """
    In-memory implementation of conversation history.
    """

    def __init__(self, max_messages: int = 10):
        self.messages = deque(maxlen=max_messages)

    def add_message(self, role: str, content: str) -> None:
        self.messages.append(
            {
                "role": role,
                "content": content,
            }
        )

    def add_user_message(self, message: str) -> None:
        self.add_message("user", message)

    def add_assistant_message(self, message: str) -> None:
        self.add_message("assistant", message)

    def get_messages(self) -> list[dict[str, str]]:
        return list(self.messages)

    def get_context(self) -> str:
        """
        Convert the conversation history into text.
        """

        if not self.messages:
            return ""

        lines = []

        for message in self.messages:
            lines.append(f"{message['role'].title()}: {message['content']}")

        return "\n".join(lines)

    def clear(self) -> None:
        self.messages.clear()
