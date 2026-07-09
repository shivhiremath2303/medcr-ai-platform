from pydantic import BaseModel


class SourceResponse(BaseModel):
    """
    Source supporting the generated answer.
    """

    filename: str
    page_number: int


class AnswerResponse(BaseModel):
    """
    Response returned by the RAG endpoint.
    """

    answer: str
    sources: list[SourceResponse] = []
