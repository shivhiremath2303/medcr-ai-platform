from dataclasses import dataclass
from typing import Optional


@dataclass
class Metadata:
    filename: str
    page_number: int
    section: str | None = None
