import numpy as np
from uuid import uuid4
from typing import List, Optional

from app.domain.models import Chunk, Document, Metadata
from app.domain.repositories.chunker import Chunker
from app.domain.repositories.embedding_repository import EmbeddingRepository


class SemanticChunkerAdapter(Chunker):
    """
    Advanced Semantic Chunker that uses embedding distances to find natural
    thematic breaks in legal documents.
    Implements Milestone 10.5.1.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingRepository,
        buffer_size: int = 1,
        breakpoint_percentile_threshold: float = 95.0,
    ):
        self.embedding_provider = embedding_provider
        self.buffer_size = buffer_size
        self.breakpoint_percentile_threshold = breakpoint_percentile_threshold

    def split_document(self, document: Document) -> List[Chunk]:
        """
        Split a document into chunks based on semantic similarity.
        """
        all_chunks: List[Chunk] = []

        for page in document.pages:
            # 1. Split into sentences (simple split for now, can be improved with regex/NLP)
            sentences = self._split_into_sentences(page.text)
            if not sentences:
                continue

            # 2. Combine sentences with buffer for context
            combined_sentences = self._combine_sentences(sentences, self.buffer_size)

            # 3. Generate embeddings for combined sentences
            # Note: DocumentService calls this, we should ideally use async version
            # but Chunker interface is currently sync. We use sync fallback for now.
            embeddings = self.embedding_provider.embed_documents(combined_sentences)

            # 4. Calculate distances between consecutive sentence embeddings
            distances = self._calculate_distances(embeddings)

            # 5. Identify breakpoints based on distance spikes
            breakpoint_indices = self._identify_breakpoints(distances)

            # 6. Group sentences into semantic chunks
            semantic_groups = self._group_sentences(sentences, breakpoint_indices)

            for group_text in semantic_groups:
                if not group_text.strip():
                    continue

                all_chunks.append(
                    Chunk(
                        chunk_id=str(uuid4()),
                        document_id=document.document_id,
                        text=group_text,
                        metadata=Metadata(
                            filename=document.filename,
                            page_number=page.page_number,
                            section=None,
                            tenant_id=document.tenant_id,
                        ),
                    )
                )

        return all_chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        # Simple sentence splitter. Legal documents can be complex,
        # so we split by common sentence enders followed by space.
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _combine_sentences(self, sentences: List[str], buffer: int) -> List[str]:
        combined = []
        for i in range(len(sentences)):
            start = max(0, i - buffer)
            end = min(len(sentences), i + buffer + 1)
            combined.append(" ".join(sentences[start:end]))
        return combined

    def _calculate_distances(self, embeddings: List[List[float]]) -> List[float]:
        distances = []
        for i in range(len(embeddings) - 1):
            emb1 = np.array(embeddings[i])
            emb2 = np.array(embeddings[i+1])
            # Cosine distance = 1 - cosine similarity
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            distances.append(1 - similarity)
        return distances

    def _identify_breakpoints(self, distances: List[float]) -> List[int]:
        if not distances:
            return []

        threshold = np.percentile(distances, self.breakpoint_percentile_threshold)
        return [i for i, d in enumerate(distances) if d > threshold]

    def _group_sentences(self, sentences: List[str], breakpoint_indices: List[int]) -> List[str]:
        groups = []
        start_idx = 0

        for bp_idx in breakpoint_indices:
            group = " ".join(sentences[start_idx : bp_idx + 1])
            groups.append(group)
            start_idx = bp_idx + 1

        # Add the last group
        groups.append(" ".join(sentences[start_idx:]))
        return groups
