import fitz  # type: ignore # PyMuPDF


class DocumentReader:
    """
    Reads documents and extracts raw text.
    """

    def read_pdf(self, file_path: str) -> str:
        """
        Extract text from a PDF file.
        """

        document = fitz.open(file_path)

        text = ""

        for page in document:
            text += page.get_text()

        document.close()

        return text
