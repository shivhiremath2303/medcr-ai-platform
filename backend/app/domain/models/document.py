from dataclasses import dataclass
from typing import List

from .page import Page


@dataclass
class Document:
    document_id: str
    filename: str
    pages: List[Page]

    @property
    def page_count(self) -> int:
        return len(self.pages)
