from dataclasses import dataclass
from typing import Optional


@dataclass
class Metadata:
    filename: str
    page_number: int
    section: str | None = None
    tenant_id: str | None = None  # Multi-Tenant Isolation (10.4.4)
