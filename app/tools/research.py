from pydantic import BaseModel, Field

from app.integrations.rag.client import RAGClient


class ResearchSearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)
    top_k: int = Field(default=5, ge=1, le=10)


rag_client = RAGClient()


def search_projects(
    query: str,
    top_k: int = 5,
) -> list[dict]:

    request = ResearchSearchRequest(
        query=query,
        top_k=top_k,
    )

    return rag_client.search_projects(
        query=request.query,
        top_k=request.top_k,
    )
