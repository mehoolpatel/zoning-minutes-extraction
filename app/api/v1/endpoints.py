#from pydantic import BaseModel
#from app.pipeline.embeddings.embedder import Embedder
#from app.pipeline.vectorstores.chroma_store import ChromaVectorStore
#from app.pipeline.vectorstores.memory_store import MemoryVectorStore
#import logging

from fastapi import APIRouter, Request, HTTPException
from app.pipeline.ingestion_pipeline import run_ingestion_pipeline
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health", 
            summary="Service Health Check", 
            description="Returns the current status and version of the API to verify the service is operational.")
def health():
    """Versioned health check."""
    return {"status": "ok", "version": "v1"}



@router.post("/ingest", 
             summary="Trigger Document Ingestion", 
             description="""
Processes the document corpus (PDFs) through the pipeline:
1. Extraction: LLM-powered parsing of zoning minutes.
2. Vectorization: Embedding text into the vector database.
3. Persistence: Saving structured relational data to SQLite.
             """)
def trigger_ingestion(request: Request, use_mock: bool = False):
    """Triggers the pipeline and uses the active store."""
    try:
        # Get the CURRENT active store from state
        active_store = request.app.state.vector_store                
        
        # Run pipeline using the current store
        extractions, updated_store, num_docs, total_pages, total_items = run_ingestion_pipeline(
            vector_store=active_store, 
            use_mock=use_mock
        )
        
        # CRITICAL: Update the state with the returned store instance
        # Even if it's the same instance, this guarantees the app uses
        # the latest version of the store.
        request.app.state.vector_store = updated_store
        count = updated_store.count()

        return {
            "status": "success",
            "processed_documents": num_docs,
            "total_pages": total_pages,
            "extractions_found": total_items
        }
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 
