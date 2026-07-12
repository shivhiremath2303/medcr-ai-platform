import os
from pathlib import Path
from typing import Any, Dict

from app.core.observability.health import HealthCheck


class StorageHealthCheck(HealthCheck):
    def __init__(self, upload_dir: Path):
        self.upload_dir = upload_dir

    @property
    def name(self) -> str:
        return "storage"

    async def check(self) -> Dict[str, Any]:
        try:
            # Check if upload directory is writable
            if not self.upload_dir.exists():
                self.upload_dir.mkdir(parents=True, exist_ok=True)

            test_file = self.upload_dir / ".health_check"
            test_file.touch()
            test_file.unlink()

            return {"status": "up", "path": str(self.upload_dir)}
        except Exception as e:
            return {"status": "down", "error": str(e)}
