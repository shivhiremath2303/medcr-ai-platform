import json
from typing import Dict, List, Optional

from app.core.observability.context import get_tenant_id, get_user_id
from app.domain.repositories.conversation_repository import ConversationRepository
from app.infrastructure.storage.redis_client import RedisClient


class RedisConversationRepository(ConversationRepository):
    """
    Redis implementation of conversation history.
    Each user has their own message list in Redis, isolated by tenant (10.4.5).
    """

    def __init__(
        self, redis_client: RedisClient, ttl: int = 3600 * 24, max_messages: int = 10
    ):
        self.redis_wrapper = redis_client
        self.ttl = ttl
        self.max_messages = max_messages
        self.key_prefix = "conv:"

    def _get_key(self) -> str:
        user_id = get_user_id() or "anonymous"
        tenant_id = get_tenant_id() or "global"
        return f"{self.key_prefix}{tenant_id}:{user_id}"

    def add_message(self, role: str, content: str) -> None:
        key = self._get_key()
        client = self.redis_wrapper.client

        message_data = {"role": role, "content": content}

        # Add to list
        client.rpush(key, json.dumps(message_data))

        # Trim to max messages
        client.ltrim(key, -self.max_messages, -1)

        # Set expiration
        client.expire(key, self.ttl)

    def add_user_message(self, message: str) -> None:
        self.add_message("user", message)

    def add_assistant_message(self, message: str) -> None:
        self.add_message("assistant", message)

    def get_messages(self) -> List[Dict[str, str]]:
        key = self._get_key()
        client = self.redis_wrapper.client

        messages = client.lrange(key, 0, -1)
        return [json.loads(m) for m in messages]

    def get_context(self) -> str:
        messages = self.get_messages()
        if not messages:
            return ""

        lines = []
        for message in messages:
            lines.append(f"{message['role'].title()}: {message['content']}")

        return "\n".join(lines)

    def clear(self) -> None:
        key = self._get_key()
        self.redis_wrapper.client.delete(key)
