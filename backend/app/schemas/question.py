from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    """
    Request model for asking questions about uploaded documents.
    """

    question: str = Field(
        ...,
        min_length=1,
        description="The user's question.",
    )

    k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of relevant chunks to retrieve.",
    )
