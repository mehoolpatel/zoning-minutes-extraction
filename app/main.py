from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1.endpoints import router as api_router
from app.api.v1.analytics import router as analytics_router
from app.pipeline.embeddings.embedder import Embedder

# Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Logic ---
    # Initialize the embedder model (needs to be done once)
    embedder = Embedder(provider="local")
    app.state.vector_store = None
    print("Vector store state initialized to None.")
    
    yield 
    
    # Clean up resources if needed
    print("Shutting down.")

app = FastAPI(
    title="Zoning Governance Analytics Platform",
    description="""
    A high-precision extraction and analytics API for municipal zoning records.
    
    Key Features:

    * Structured Extraction: Converts narrative PDF minutes into relational data.
    * Auditability: Links every record back to its source document and page.
    * Member Analytics: Tracks voting patterns and tenure across sessions.
    """,
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "Project Submission",
        "url": "https://github.com/your-repo-link",
    },
)

app.include_router(api_router, prefix="/api/v1", tags=["document ingestion"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])
