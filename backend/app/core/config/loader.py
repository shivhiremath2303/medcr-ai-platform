import os
import sys
from functools import lru_cache
from typing import Dict, Type

from app.core.config.base import Settings
from app.core.config.development import DevelopmentSettings
from app.core.config.production import ProductionSettings
from app.core.config.testing import TestingSettings
from app.core.config.validation import validate_config

_environments: Dict[str, Type[Settings]] = {
    "development": DevelopmentSettings,
    "testing": TestingSettings,
    "production": ProductionSettings,
}


@lru_cache
def get_settings() -> Settings:
    """
    Returns the appropriate settings object based on the ENVIRONMENT variable.
    Ensures validation passes before returning.
    """
    env = os.getenv("ENVIRONMENT", "development").lower()
    config_class = _environments.get(env, DevelopmentSettings)

    try:
        settings = config_class()
        validate_config(settings)
        return settings
    except Exception as e:
        # Fail fast with a clear error message to stderr
        print(
            f"\nCRITICAL ERROR: Configuration failed for environment '{env}'",
            file=sys.stderr,
        )
        print(f"Details: {e}\n", file=sys.stderr)
        sys.exit(1)
