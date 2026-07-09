import fitz


class PDFExtractor:
    """
    Service responsible for extracting text from PDF files.
    """

    def extract_text(self, file_path: str) -> str:
        """
        Extract all text from a PDF.

        Args:
            file_path: Path to the PDF file.

        Returns:
            Entire document as a single string.
        """

        document = fitz.open(file_path)

        pages = []

        for page in document:
            text = page.get_text()
            pages.append(text)

        document.close()

        return "\n".join(pages)