from .memory_store import MemoryVectorStore
from .chroma_store import ChromaVectorStore  

def get_vector_store(provider="memory", embedding_model=None, persist_dir="./chroma_db"):
    if provider == "memory":
        if embedding_model is None:
            raise ValueError("MemoryStore requires an embedding model")
        return MemoryVectorStore(embedding_model)
    elif provider == "chroma":
        if embedding_model is None:
            raise ValueError("ChromaStore requires a callable embedding function")
        return ChromaVectorStore(persist_dir, embedding_model)
    else:
        raise ValueError(f"Unknown provider: {provider}")