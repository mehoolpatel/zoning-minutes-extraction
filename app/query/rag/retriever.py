from typing import List, Tuple
from app.pipeline.vectorstores.vector_store import VectorStore
from app.pipeline.embeddings.embedder import Embedder

class Retriever:
    """
    Thin wrapper around VectorStore + Embedder.
    Finds top-k most similar chunks for a query.
    """

    def __init__(self, vector_store: VectorStore, embedder: Embedder):
        self.vector_store = vector_store
        self.embedder = embedder

    def search(self, query: str, k: int = 5) -> List[Tuple[str, dict]]:
        """
        Returns [(chunk_text, metadata), ...]
        """
        query_vector = self.embedder.embed(query)
        results = self.vector_store.search(query_vector, k)
        return [(item.chunk.content, item.chunk.metadata) for item in results]