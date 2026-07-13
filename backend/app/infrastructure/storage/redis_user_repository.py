import json
from typing import List, Optional
from app.domain.models.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.storage.redis_client import RedisClient

class RedisUserRepository(UserRepository):
    """
    Distributed User Repository using Redis.
    Ensures user consistency across horizontal pods.
    Implements Milestone 10.3.5.
    """

    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client
        self.key_prefix = "user:"
        self.username_index = "users:by_username"

    def _key(self, user_id: str) -> str:
        return f"{self.key_prefix}{user_id}"

    def get_by_id(self, user_id: str) -> Optional[User]:
        data = self.redis.client.get(self._key(user_id))
        if data:
            return User.model_validate_json(data)
        return None

    def get_by_username(self, username: str) -> Optional[User]:
        user_id = self.redis.client.hget(self.username_index, username)
        if user_id:
            if isinstance(user_id, bytes):
                user_id = user_id.decode()
            return self.get_by_id(user_id)
        return None

    def save(self, user: User) -> None:
        client = self.redis.client
        pipeline = client.pipeline()
        # 1. Save user object
        pipeline.set(self._key(user.user_id), user.model_dump_json())
        # 2. Update username index
        pipeline.hset(self.username_index, user.username, user.user_id)
        pipeline.execute()

    def list_all(self) -> List[User]:
        # Note: In production, scanning keys is expensive.
        # This is for administrative compatibility.
        keys = self.redis.client.keys(f"{self.key_prefix}*")
        users = []
        for key in keys:
            data = self.redis.client.get(key)
            if data:
                users.append(User.model_validate_json(data))
        return users

    def delete(self, user_id: str) -> None:
        user = self.get_by_id(user_id)
        if not user:
            return

        client = self.redis.client
        pipeline = client.pipeline()
        pipeline.delete(self._key(user_id))
        pipeline.hdel(self.username_index, user.username)
        pipeline.execute()
