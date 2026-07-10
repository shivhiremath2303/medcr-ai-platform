from pathlib import Path
from uuid import uuid4
from docx import Document as DocxDocument
from pypdf import PdfReader

from app.core.constants import SUPPORTED_EXTENSIONS
from app.domain.models import Document, Page
from app.domain.repositories.document_parser import DocumentParser


class DocumentParserAdapter(DocumentParser):
    """
    Adapter for parsing PDF and DOCX documents.
    """

    def parse_document(self, file_path: str) -> Document:
        extension = Path(file_path).suffix.lower()

        if extension not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {extension}")

        if extension == ".pdf":
            pages = self._parse_pdf(file_path)
        else:
            pages = self._parse_docx(file_path)

        return Document(
            document_id=str(uuid4()),
            filename=Path(file_path).name,
            pages=pages,
        )

    def _parse_pdf(self, file_path: str) -> list[Page]:
        reader = PdfReader(file_path)
        pages: list[Page] = []

        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text and text.strip():
                pages.append(
                    Page(
                        page_number=index,
                        text=text,
                    )
                )
        return pages

    def _parse_docx(self, file_path: str) -> list[Page]:
        document = DocxDocument(file_path)
        paragraphs = [p.text for p in document.paragraphs if p.text.strip()]

        return [
            Page(
                page_number=1,
                text="\n".join(paragraphs),
            )
        ]
