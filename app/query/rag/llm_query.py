from typing import List, Dict, Any
from app.query.rag.retriever import Retriever
from app.pipeline.embeddings.embedder import Embedder
from app.pipeline.vectorstores.vector_store import VectorStore
from openai import OpenAI

client = OpenAI()

class RAGQueryEngine:
    """
    The complete RAG orchestration layer.
    """

    def __init__(self, vector_store: VectorStore, embedder: Embedder):
        self.retriever = Retriever(vector_store, embedder)

    def _build_prompt(self, query: str, retrieved_chunks: List[tuple]) -> str:
        """Assemble the prompt for the LLM using retrieved context."""
        context_block = "\n\n".join(
            f"Chunk {i+1}:\n{content}\nMetadata: {metadata}"
            for i, (content, metadata) in enumerate(retrieved_chunks)
        )

        return f"""
You are an assistant that answers user questions strictly based on the retrieved context.

## Retrieved Context:
{context_block}

## User Question:
{query}

## Instructions:
- Cite relevant context portions when possible.
- If the answer cannot be derived from the context, say:
  "I couldn't find this in the documents."
"""

    def run(self, query: str, k: int = 5) -> Dict[str, Any]:
        """Full RAG pipeline: retrieve → prompt → LLM → structured output."""
        retrieved = self.retriever.search(query, k=k)

        prompt = self._build_prompt(query, retrieved)

        # Call LLM
        response = client.chat.completions.create(
            #model="gpt-4.1",
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for RAG queries."},
                {"role": "user", "content": prompt},
            ],
        )

        answer = response.choices[0].message.content

        return {
            "query": query,
            "answer": answer,
            "retrieved_chunks": [
                {"content": content, "metadata": metadata} for content, metadata in retrieved
            ],
        }