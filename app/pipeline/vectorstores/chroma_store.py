from langchain_chroma import Chroma
from langchain_core.documents import Document

class ChromaVectorStore:
    """Wrapper for Chroma DB."""

    def __init__(self, persist_dir: str, embedder):
        self.embedder = embedder
        self.store = Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embedder
        )

    def count(self):
        return self.store._collection.count()

    def sample_documents2(self, n=5):
        docs = self.store._collection.get(limit=n)

        # returns list of dicts with text + metadata
        return [
            {"text": d.page_content, "metadata": d.metadata}
            for d in docs.documents
        ]

    def sample_documents(self, n=5):
        # --- FIX: Access _collection through self.store ---
        raw_docs = self.store._collection.get(limit=n, include=['documents', 'metadatas'])
        
        # Chroma .get() returns dictionaries, not LangChain Document objects
        results = []
        for i in range(len(raw_docs['ids'])):
            results.append({
                "text": raw_docs['documents'][i],
                "metadata": raw_docs['metadatas'][i]
            })
        return results

    def add_documents(self, docs: list):
        # Accepts a list of LangChain Documents
        #docs = [
        #    Document(
        #        page_content=c.content,
        #        metadata={"source_id": c.metadata.source_id, "page_number": c.metadata.page_number}
        #    )
        #    for c in chunks
        #]
        #self.store.add_documents(docs)
        lc_docs = []
        for doc in docs:
            lc_docs.append(
                Document(
                    page_content=doc.page_content,
                    metadata=doc.metadata              
                )
            )
        self.store.add_documents(lc_docs)

    def as_retriever(self):
        return self.store.as_retriever()