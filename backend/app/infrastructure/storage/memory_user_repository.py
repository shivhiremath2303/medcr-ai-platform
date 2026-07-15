from typing import Dict, List, Optional

from app.domain.models.user import User
from app.domain.repositories.user_repository import UserRepository


class MemoryUserRepository(UserRepository):
    """
    In-memory implementation of UserRepository.
    """

    def __init__(self):
        self._users: Dict[str, User] = {}

    def get_by_id(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def get_by_username(self, username: str) -> User | None:
        for user in self._users.values():
            if user.username == username:
                return user
        return None

    def get_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def save(self, user: User) -> User:
        self._users[user.user_id] = user
        return user

    def list_all(self) -> List[User]:
        return list(self._users.values())
