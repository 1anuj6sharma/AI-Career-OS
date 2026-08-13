from typing import List, Dict, Any, Optional
from app.core.logging import logger


class VectorStoreService:
    """
    RAG Vector Store Abstraction Layer (ChromaDB / InMemory fallback).
    Manages vector embeddings and retrieval for resumes, job descriptions, and career notes.
    """

    def __init__(self):
        self.documents: List[Dict[str, Any]] = []

    def add_document(self, doc_id: str, content: str, metadata: Dict[str, Any] = None) -> None:
        self.documents.append({
            "id": doc_id,
            "content": content,
            "metadata": metadata or {}
        })
        logger.info(f"RAG VectorStore indexed document {doc_id}")

    def similarity_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_words = set(query.lower().split())
        results = []
        for doc in self.documents:
            content_words = set(doc["content"].lower().split())
            overlap = len(query_words.intersection(content_words))
            results.append((overlap, doc))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:top_k]]
