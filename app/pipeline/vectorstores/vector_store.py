import numpy as np
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings 
from typing import List, Any
from langchain_core.documents import Document 
from .memory_store import MemoryVectorStore

class VectorStore:
    def __init__(self, provider: str = "chroma", persist_directory: str = "./chroma_db", embedding_model: Any = None):
        self.provider = provider
        self.embedding_model = embedding_model # Store model for local use

        if provider == "memory" and embedding_model is None:
            raise ValueError(
                "VectorStoreWrapper requires an 'embedding_model' (like sentence-transformers) "
                "when using provider='memory' to pre-compute vectors."
            )        
        if provider == "chroma":
            langchain_embedding_function = HuggingFaceEmbeddings(model_name=embedding_model) 
            self.store = Chroma(
                persist_directory=persist_directory,
                embedding_function=langchain_embedding_function   #embedding_model # Chroma handles embedding
            )
        elif provider == "memory":
            self.store = MemoryVectorStore()  # custom local class using python and numpy
        else:
            raise ValueError(f"Unknown store provider: {provider}")

    def add_documents(self, documents: List[Document]):
        # Standardize inputs to LangChain Documents for Chroma
        # and extract content/metadata for Memory Store
        
        if self.provider == "chroma":
            formatted_docs = []
            for doc in documents:
                # If it's already a LC Document
                if isinstance(doc, Document):
                    formatted_docs.append(doc)
                else:
                    # Assume it's a DocumentChunk and convert
                    formatted_docs.append(Document(
                        page_content=doc.content, # Use .content
                        metadata={
                            "source_id": doc.metadata.source_id,
                            "page_number": doc.metadata.page_number
                        }
                    ))
            self.store.add_documents(formatted_docs)
            
        elif self.provider == "memory":
            for doc in documents:
                # Robustly extract content
                if isinstance(doc, Document):
                    text = doc.page_content
                    meta = doc.metadata
                else:
                    text = doc.content
                    meta = doc.metadata # Assuming DocumentChunk has metadata

                # Calculate vector
                vector = self.embedding_model.encode(text).tolist()
                
                # Add to custom store
                self.store.add(text, meta, vector) # Adjust .add arguments as needed

    def as_retriever(self, **kwargs):
        """Generic method to get a retriever object."""
        # Note: Your custom MemoryVectorStore needs a '.search' method 
        # that mimics LangChain's retriever interface to be fully compatible.
        return self.store.as_retriever(**kwargs)