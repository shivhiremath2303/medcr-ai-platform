"""Domain models package.

This package defines simple data-holding domain entities used across the
core application. The domain layer is intentionally dependency-free (no
Pydantic/FastAPI/LangChain imports) — simple dataclasses are used.
"""
from .document import Document
from .page import Page
from .chunk import Chunk
from .metadata import Metadata
from .search_result import SearchResult

__all__ = [
    "Document",
    "Page",
    "Chunk",
    "Metadata",
    "SearchResult",
]
