from app.core.config.base import Settings

class DevelopmentSettings(Settings):
    environment: str = "development"
    debug: bool = True
    log_level: str = "DEBUG"
