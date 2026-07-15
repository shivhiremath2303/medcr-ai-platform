import bcrypt
from passlib.context import CryptContext

# passlib is unmaintained and fails to detect bcrypt version 4.1.0+ correctly
# because the __about__ attribute was removed. This monkey-patch restores it.
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("About", (object,), {"__version__": bcrypt.__version__})

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordHasher:
    """
    Utility for hashing and verifying passwords.
    """

    @staticmethod
    def hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
