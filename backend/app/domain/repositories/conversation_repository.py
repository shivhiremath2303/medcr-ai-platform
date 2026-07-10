from abc import ABC, abstractmethod


class ConversationRepository(ABC):
    """
    Repository contract for conversation history.
    """

    @abstractmethod
    def add_message(self, role: str, content: str) -> None:
        """Append a message to the conversation history."""

    @abstractmethod
    def add_user_message(self, message: str) -> None:
        """Append a user message."""

    @abstractmethod
    def add_assistant_message(self, message: str) -> None:
        """Append an assistant message."""

    @abstractmethod
    def get_messages(self) -> list[dict[str, str]]:
        """Return the stored conversation history."""

    @abstractmethod
    def get_context(self) -> str:
        """Return the conversation history as prompt text."""

    @abstractmethod
    def clear(self) -> None:
        """Remove all stored conversation history."""
