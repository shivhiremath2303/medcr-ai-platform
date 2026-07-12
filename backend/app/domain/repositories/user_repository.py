from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.models.user import User


class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve a user by ID."""

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by username."""

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by email."""

    @abstractmethod
    def save(self, user: User) -> User:
        """Save a user."""

    @abstractmethod
    def list_all(self) -> List[User]:
        """List all users."""
