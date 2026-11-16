import httpx

from app.config import settings


class RAGClient:
    """
    Client for the enterprise-hybrid-rag service
    (hybrid retrieval over EU research projects from CORDIS).
    """

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.RAG_API_URL).rstrip("/")

    def search_projects(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:

        response = httpx.get(
            f"{self.base_url}/search",
            params={
                "q": query,
                "top_k": top_k,
            },
            timeout=30.0,
        )

        response.raise_for_status()

        return [
            {
                "title": hit["title"],
                "grant_id": hit["document_id"],
                "url": f"https://cordis.europa.eu/project/id/{hit['document_id']}",
                "relevance": round(hit["rerank_score"], 3),
                "excerpt": hit["text"],
            }
            for hit in response.json()
        ]
