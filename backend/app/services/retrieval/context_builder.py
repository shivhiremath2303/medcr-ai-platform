from app.domain.models import SearchResult

class ContextBuilder:
    """
    Builds LLM context from retrieval results.

    This service is responsible only for transforming
    retrieval results into prompt-ready context.
    """

    @staticmethod
    def build(
        results: list[SearchResult],
    ) -> str:
        """
        Convert retrieval results into a context string.
        """

        if not results:
            return ""

        context_parts: list[str] = []

        for result in results:

            metadata = result.chunk.metadata

            context_parts.append(
                (
                    f"[Source {result.rank}]\n"
                    f"File: {metadata.filename}\n"
                    f"Page: {metadata.page_number}\n\n"
                    f"{result.chunk.text}"
                )
            )

        return "\n\n".join(context_parts)
