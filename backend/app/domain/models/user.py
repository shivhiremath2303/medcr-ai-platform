from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class UserRole(str, Enum):
    ADMIN = "admin"
    LAWYER = "lawyer"
    PARALEGAL = "paralegal"
    REVIEWER = "reviewer"
    READ_ONLY = "readonly"


@dataclass
class User:
    user_id: str
    username: str
    email: str
    hashed_password: str
    role: UserRole
    is_active: bool = True
    full_name: Optional[str] = None
