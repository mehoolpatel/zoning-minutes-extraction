import numpy as np
from typing import List
from langchain_core.documents import Document

class MemoryVectorStore:
    """In-memory vector store with cosine similarity search."""

    def __init__(self, embedding_model):                
        self.items = []
        self.embedding_model = embedding_model 

    def count(self):
        return len(self.items)
    
    def add(self, text, metadata):
        vector = self.embedding_model.embed(text)
        self.items.append((text, metadata, vector))

    #def add_documents(self, documents: List[Document]):
    #    for doc in documents:
    #        # Generate embedding and add to self.items
    #        vector = self.embedding_function(doc.page_content)                
    #        self.items.append((doc.page_content, doc.metadata, vector))

    def add_documents(self, documents: List[Document]):
        for doc in documents:
            vector = self.embedding_model.embed(doc.page_content)
            self.items.append((doc.page_content, doc.metadata, vector))

    def sample_documents(self, n=5):
        """
        Return a sample of stored documents, including text and metadata.
        """
        # Take first n items or all if fewer
        n = min(n, len(self.items))
        sample = self.items[:n]

        # Convert to list of dicts
        results = []
        for text, metadata, _ in sample:
            results.append({
                "text": text,
                "metadata": metadata
            })
        return results

    def __len__(self):
        return len(self.items)
    
    def search(self, query_embedding, top_k=3):
        if not self.items:
            return []

        # Unpack embeddings
        chunks, _, embeddings = zip(*self.items)

        # Convert to numpy arrays for vectorized math
        emb_matrix = np.array(embeddings)
        q_vec = np.array(query_embedding)

        # Cosine similarity
        dot_products = emb_matrix @ q_vec
        norms = np.linalg.norm(emb_matrix, axis=1) * np.linalg.norm(q_vec)
        scores = np.divide(dot_products, norms, out=np.zeros_like(dot_products), where=norms!=0)    

        # Get top K results
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [chunks[i] for i in top_indices]
    
    def search0(self, query_embedding, top_k=3):
        if not self.items:
            return []
            
        # Convert to numpy arrays for vectorized math
        q_vec = np.array(query_embedding)
        texts, embeddings = zip(*self.items)
        emb_matrix = np.array(embeddings)
            
        # Calculate Cosine Similarity: (A . B) / (||A|| * ||B||)
        # The '@' operator performs matrix-vector multiplication
        dot_products = emb_matrix @ q_vec
        norms = np.linalg.norm(emb_matrix, axis=1) * np.linalg.norm(q_vec)
            
        # Avoid division by zero if an embedding is all zeros
        scores = np.divide(dot_products, norms, out=np.zeros_like(dot_products), where=norms!=0)
            
        # Get top K indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        return [texts[i] for i in top_indices]
