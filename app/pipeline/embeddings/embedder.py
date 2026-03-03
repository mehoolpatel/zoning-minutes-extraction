import os
import logging
from typing import List
from sentence_transformers import SentenceTransformer
import openai

logger = logging.getLogger(__name__)

import os
import logging
from typing import List
from sentence_transformers import SentenceTransformer
import openai

logger = logging.getLogger(__name__)

class Embedder:
    def __init__(self, provider: str = "local"):
        self.provider = provider
        logger.info(f"Initializing Embedder with provider: {provider}")
        
        if provider == "local":
            # Load the model
            self.model = SentenceTransformer("all-MiniLM-L6-v2")   
            # Determine the dimension!
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Local embedding model loaded. Dimension: {self.dimension}")
                
        elif provider == "openai":
            self.client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            self.model_name = "text-embedding-3-small"
            # OpenAI is safe to hardcode IF you know the model version, but you can also get this from the API response if needed.
            self.dimension = 1536 
        else:
            raise ValueError(f"Unknown embedding provider: {provider}")

    def embed(self, text: str) -> List[float]:
        # ... rest of your embed method remains the same ...
        if not text.strip():                
            return [0.0] * self.dimension                

        if self.provider == "local":
            return self.model.encode(text).tolist()
            
        elif self.provider == "openai":
            response = self.client.embeddings.create(
                model=self.model_name,
                input=text
            )
            return response.data[0].embedding
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.model.encode([text])[0].tolist()
