from pathlib import Path

import pytest

from app.domain.models.document import Document
from app.infrastructure.parser.document_parser_adapter import DocumentParserAdapter


def test_parse_pdf(fixtures_dir: Path):
    """
    Verify that a PDF document is parsed successfully.
    """

    pdf_file = fixtures_dir / "sample.pdf"
    parser = DocumentParserAdapter(supported_extensions={".pdf", ".docx"})

    document = parser.parse_document(
        str(pdf_file),
    )

    assert isinstance(document, Document)
    assert document.filename == "sample.pdf"
    assert document.page_count > 0
    assert len(document.pages) > 0


def test_parse_docx(fixtures_dir: Path):
    """
    Verify that a DOCX document is parsed successfully.
    """

    docx_file = fixtures_dir / "sample.docx"
    parser = DocumentParserAdapter(supported_extensions={".pdf", ".docx"})

    document = parser.parse_document(
        str(docx_file),
    )

    assert isinstance(document, Document)
    assert document.filename == "sample.docx"
    assert document.page_count > 0
    assert len(document.pages) > 0


def test_unsupported_file_type(tmp_path: Path):
    """
    Unsupported file types should raise ValueError.
    """

    file = tmp_path / "sample.txt"
    parser = DocumentParserAdapter(supported_extensions={".pdf", ".docx"})

    file.write_text("Hello World")

    with pytest.raises(ValueError):
        parser.parse_document(
            str(file),
        )
