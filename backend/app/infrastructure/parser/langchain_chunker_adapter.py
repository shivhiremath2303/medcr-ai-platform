from uuid import uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.domain.models import Chunk, Document, Metadata
from app.domain.repositories.chunker import Chunker


class LangChainChunkerAdapter(Chunker):
    """
    Adapter for LangChain's RecursiveCharacterTextSplitter.
    Enhanced with Multi-Tenant awareness (10.4.4).
    """

    def __init__(
        self,
        chunk_size: int,
        chunk_overlap: int,
    ):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def split_document(self, document: Document) -> list[Chunk]:
        chunks: list[Chunk] = []

        for page in document.pages:
            page_chunks = self.splitter.split_text(page.text)

            for chunk_text in page_chunks:
                chunks.append(
                    Chunk(
                        chunk_id=str(uuid4()),
                        document_id=document.document_id,
                        text=chunk_text,
                        metadata=Metadata(
                            filename=document.filename,
                            page_number=page.page_number,
                            section=None,
                            tenant_id=document.tenant_id,  # Preserve isolation (10.4.4)
                        ),
                    )
                )

        return chunks
