from pydantic import BaseModel


class DocumentPage(BaseModel):
    """
    Represents a single page extracted from a document.
    """

    page_number: int
    text: str
