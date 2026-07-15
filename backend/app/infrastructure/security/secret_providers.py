import os
from pathlib import Path
from typing import Dict, Optional

from app.core.observability.logger import get_logger
from app.domain.repositories.security.secret_provider import SecretProvider

logger = get_logger(__name__)


class MultiSourceSecretProvider(SecretProvider):
    """
    Enterprise secret provider that aggregates multiple sources.
    Priority:
    1. Docker Secrets / File-based (/run/secrets/)
    2. Environment Variables
    """

    def __init__(self, secrets_dir: str = "/run/secrets"):
        self.secrets_dir = Path(secrets_dir)
        self._cache: Dict[str, str] = {}

    def get_secret(self, key: str, default: str | None = None) -> str | None:
        # 1. Check Cache
        if key in self._cache:
            return self._cache[key]

        # 2. Check File-based (Docker Secrets)
        # We look for a file named exactly like the key (often uppercase)
        file_path = self.secrets_dir / key
        if file_path.exists() and file_path.is_file():
            try:
                value = file_path.read_text().strip()
                self._cache[key] = value
                logger.debug(f"Loaded secret '{key}' from file source")
                return value
            except Exception as e:
                logger.error(f"Failed to read secret file {file_path}: {e}")

        # 3. Check Environment
        env_value = os.getenv(key)
        if env_value is not None:
            # We don't cache env values to support dynamic rotation if the env changes
            # (though env rotation usually requires restart anyway, it's safer)
            return env_value

        return default

    def refresh(self) -> None:
        """Clear cache to force re-reading from files/vaults."""
        logger.info("Refreshing secrets cache")
        self._cache.clear()


class VaultSecretProvider(SecretProvider):
    """
    Placeholder for professional Vault integration (HashiCorp, AWS, etc).
    This demonstrates readiness for enterprise-scale secret management.
    """

    def get_secret(self, key: str, default: str | None = None) -> str | None:
        # In a real implementation, this would call the Vault API/SDK
        return default

    def refresh(self) -> None:
        pass
