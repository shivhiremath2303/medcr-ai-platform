from uuid import uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.constants import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
)
from app.domain.models import Chunk as DomainChunk
from app.domain.models import Document
from app.domain.models import Metadata
from app.schemas.chunk import Chunk, ChunkMetadata


class DocumentChunker:
    """
    Splits documents into semantic chunks.

    During the Milestone 4 migration this service exposes both
    the legacy schema-based API and the new domain-model API.
    """

    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
    ):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                "",
            ],
        )

    # ----------------------------------------------------------
    # Legacy API
    # ----------------------------------------------------------

    def split(
        self,
        text: str,
        document_name: str,
    ) -> list[Chunk]:
        """
        Legacy chunking API.

        Returns schema-based chunks for compatibility
        with the Milestone 3 pipeline.
        """

        text_chunks = self.splitter.split_text(text)

        chunks: list[Chunk] = []

        for index, chunk_text in enumerate(text_chunks):
            chunks.append(
                Chunk(
                    text=chunk_text,
                    metadata=ChunkMetadata(
                        document_name=document_name,
                        page_number=1,
                        chunk_id=index,
                    ),
                )
            )

        return chunks

    # ----------------------------------------------------------
    # New Production API
    # ----------------------------------------------------------

    def split_document(
        self,
        document: Document,
    ) -> list[DomainChunk]:
        """
        Splits a Document domain model into metadata-aware chunks.
        """

        chunks: list[DomainChunk] = []

        for page in document.pages:

            page_chunks = self.splitter.split_text(page.text)

            for chunk_text in page_chunks:

                chunks.append(
                    DomainChunk(
                        chunk_id=str(uuid4()),
                        document_id=document.document_id,
                        text=chunk_text,
                        metadata=Metadata(
                            filename=document.filename,
                            page_number=page.page_number,
                            section=None,
                        ),
                    )
                )

        return chunks
