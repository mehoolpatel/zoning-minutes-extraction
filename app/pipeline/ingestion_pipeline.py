import logging
import json
from typing import List, Dict, Any
from app.pipeline.loaders import load_documents
from app.pipeline.extractors import get_extractor
from app.pipeline.vectorstores import get_vector_store
from app.pipeline.embeddings.embedder import Embedder
from app.pipeline.chunkers.chunker import DocumentChunker 
from app.query.structured.crud import ingest_extraction_result
from app.core.db import SessionLocal
from app.core.schemas import ExtractionResult 
from sqlalchemy.orm import Session
from langchain_core.documents import Document
from app.core.schemas import DocumentChunk, ExtractionResult


# Configure logging to see output in your terminal
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Silence third-party noise
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

# ----------- Helper to store into SQL db  ----------

def sql_store_extraction_results(db: Session, extraction_results: List[ExtractionResult]):
    """Helper function to flatten and insert extraction results into SQL DB."""
    for result in extraction_results:   
        ingest_extraction_result(db, result)

# ----------- Ingestion pipeline --------------------
def run_ingestion_pipeline(vector_store=None, use_mock: bool = True):
    """
    Ingestion pipeline:
    Load → Chunk → Extract → Embed → Store
    Returns (list_of_extractions, vector_store)
    """
    # Initialization and configuration
    all_extractions = []
    chunker = DocumentChunker(chunk_size=999)  # chunk_size = pages (set high number for "Whole Document" mode)
    extractor = get_extractor(use_mock=False)    
    embedder = Embedder(provider="local")    

    # If a vector_store was passed in, use it, otherwise create a new one
    if vector_store is None:
        # initialize the vector store (local "memory" or "chroma")
        vector_store = get_vector_store(provider="chroma", embedding_model=embedder)
        logger.info(f"vector_store init to chroma")
    else:
        logger.info(f"vector_store is already set.")

    db = SessionLocal() # Create the session manually

    # Load → Chunk (once outside the loop)
    docs = load_documents(use_mock=False, dump_pages=True)
    logger.info(f"Loaded {len(docs)} documents.")

    chunks = chunker.chunk(docs)
    logger.info(f"Processing {len(chunks)} chunks...")

    # Process and Store Chunks: Extract → Embed → Store
    for loop_cnt, chunk in enumerate(chunks, start=1):
        logger.info(f"Processing chunk {loop_cnt} of {len(chunks)}...")

        # Extract structured actions/votes from this chunk
        extraction_results = extractor.extract([chunk])

        # Need to generate a document id
        for res in extraction_results:
            if res.document_id == 'unknown':
                # Map the Pydantic metadata 'file_name' to the result's 'document_id'
                res.document_id = getattr(chunk.metadata, 'file_name', 'unknown')

        # Store structured extractions from the chunk in SQL Database
        sql_store_extraction_results(db, extraction_results)

        # Attach extraction to metadata
        chunk.metadata.extraction = extraction_results
        
        # Extract text content and metadata, handling both custom chunks and LangChain Documents
        text = chunk.content
        meta = chunk.metadata.model_dump() # Convert Pydantic model to a dict
        meta["extraction"] = json.dumps(meta["extraction"])
    
        # Create a LangChain Document object. Embed and add to vector store.
        lang_doc = Document(page_content=text, metadata=meta)

        vector_store.add_documents([lang_doc])
        all_extractions.extend(extraction_results)

    logger.info(f"Ingestion complete. Extracted {len(all_extractions)} items.")    
    return all_extractions, vector_store

if __name__ == "__main__":
    extractions, store = run_ingestion_pipeline(use_mock=True)
    logger.info("Sample Extractions:")
    for e in extractions[:5]:  # just first 5 for brevity
        logger.info(e)
    logger.info(f"Vector store contains {len(store)} chunks")

    # Inspect the first item to verify structure
    if len(store) > 0:
        first_chunk, first_vector = store.items[0]
        logger.info("--- Sample Data Inspection ---")
        logger.info(f"Chunk Text: {first_chunk.content}")
        logger.info(f"Metadata: {first_chunk.metadata}")
        logger.info(f"Vector Dim: {len(first_vector)}") 
        logger.info("-----------------------------")