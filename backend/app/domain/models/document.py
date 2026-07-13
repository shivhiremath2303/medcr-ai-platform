from dataclasses import dataclass
from typing import List, Optional

from .page import Page


@dataclass
class Document:
    document_id: str
    filename: str
    pages: List[Page]
    owner_id: Optional[str] = None  # Enterprise Hardening: Resource ownership

    @property
    def page_count(self) -> int:
        return len(self.pages)
