from collections import deque


class ConversationMemory:
    """
    Stores the recent conversation history.
    """

    def __init__(self, max_messages: int = 10):
        self.messages = deque(maxlen=max_messages)

    def add_user_message(self, message: str) -> None:
        self.messages.append(
            {
                "role": "user",
                "content": message,
            }
        )

    def add_assistant_message(self, message: str) -> None:
        self.messages.append(
            {
                "role": "assistant",
                "content": message,
            }
        )

    def get_messages(self) -> list[dict]:
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
