from dataclasses import dataclass
from typing import List, Optional

from .page import Page


@dataclass
class Document:
    document_id: str
    filename: str
    pages: List[Page]
    owner_id: str | None = None  # Enterprise Hardening: Resource ownership
    tenant_id: str | None = None # Multi-Tenant Isolation (10.4.4)

    @property
    def page_count(self) -> int:
        return len(self.pages)
