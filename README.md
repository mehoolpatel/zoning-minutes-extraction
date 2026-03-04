# Zoning Governance Analytics Platform

## Overview
The **Zoning Governance Analytics Platform** is a specialized document intelligence engine designed to transform unstructured Municipal Zoning Meeting Minutes (PDFs) into a high-fidelity relational database. 

By leveraging LLM-based structured extraction and entity resolution, the platform reconciles board member identities and maps complex voting patterns across multiple years of municipal records, providing deep insights into local governance.

## 🧠 Advanced Document Intelligence
- **Cross-Document Entity Resolution**: Automatically reconciles fragmented or partial member names (e.g., "Timler," "J. Timler") into unique, unified entities (e.g., "Jeff Timler") across the entire document corpus.
- **Relational Mapping**: Maps "Meeting Items" (Cases, Motions, Approvals) to specific "Member Votes" with a structured schema, bypassing the limitations of standard text-based RAG.
- **Context-Aware Analytics**: Tracks member "Tenure" (First/Last Seen) and aggregate voting records (Yes/No/Abstain/Absent) across different meeting types.

## 🛠 Setup & Installation

### 1. Python Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
### 2. Environment Configuration
Create a `.env` file in the root directory. This project requires an OpenAI API key for the structured extraction pipeline:

```bash
# .env
OPENAI_API_KEY=your_sk_...
```

## 🚀 Running the Platform

### 1. Start the API
Launch the FastAPI server using uvicorn:
```bash
uvicorn app.main:app --reload
```

### 2. Run the Ingestion Pipeline
1. Navigate to the Swagger UI: `http://127.0.0.1:8000/docs`.
2. Locate the **POST** `/api/v1/ingest` endpoint.
3. Click **"Try it out"**.
4. The pipeline defaults to live PDF ingestion (use_mock=False).
5. Execute the request. This will trigger the pipeline to process the 6 PDFs located in `/data/pdfs` through the LLM extraction engine. 
   * **Note**: Processing the full 25-page corpus takes approximately **4-5 minutes**. You can monitor progress in the server terminal.

### 3. Explore the Analytics

Once ingestion is complete, use the following endpoints to verify the structured data and board member profiles. These endpoints allow you to pivot between member voting history and specific zoning case outcomes:

* **Member Directory**: `GET /api/v1/analytics/members`
    * *List all unique board members identified across the corpus, including their "First Seen" and "Last Seen" dates.*
* **Member Statistics**: `GET /api/v1/analytics/members/{id}`
    * *View aggregate voting records (Yes/No/Abstain/Absent) for a specific board member.*
* **Votes Timeline**: `GET /api/v1/analytics/votes`
    * *A filterable stream of individual votes cast, allowing for analysis by date, member, or item type.*
* **Meeting Item Registry**: `GET /api/v1/analytics/meeting-items`
    * *List all extracted zoning cases and agenda items, including the final action taken and total vote counts.*
* **Item Detail Deep-Dive**: `GET /api/v1/analytics/meeting-items/{id}`
    * *Access full case details, including applicants, property locations, zoning districts, and the specific motion history.*

> **Note:** For full request/response schemas and available query parameters (limits, date filters, etc.), please refer to the [API Documentation](./API.md).

## ⚠️ Known Issues & Limitations

* **Idempotency**: The ingestion pipeline does not currently track "already processed" files. To avoid duplicate records, use the provided `reset_db.py` script or delete the `.db` file before re-running ingestion.
* **In-Memory Vector Store**: The current configuration uses an in-memory instance of ChromaDB for speed. Data in the vector store is not persisted across server restarts.

## 🛠 Project Structure

```text
rag-document-extraction-pipeline/
├── app/
│   ├── api/             # FastAPI routers and v1 endpoint definitions
│   ├── core/            # Database config, prompt templates, and Pydantic schemas
│   ├── models/          # SQLAlchemy ORM models (Structured SQL Data)
│   ├── pipeline/        # Ingestion logic: loaders, extractors, and chunkers
│   ├── query/           # Database aggregation and analytics logic
│   └── main.py          # FastAPI application entry point
├── data/
│   ├── pdfs/            # Source Zoning Document corpus (Ingestion Target)
│   ├── debug/           # Extracted text dumps (useful for pipeline verification)
│   └── data/mock_ocr_outputs/ # (Deprecated) Baseline JSON data used during initial development
├── diagrams/            # Architecture and ERD visualizations
├── tests/               # Unit and integration tests for OpenAI and Extractors
├── reset_db.py         # Utility to wipe SQLite and Vector DBs for a clean start
├── requirements.txt    # Project dependencies
├── DESIGN.md           # High-level architecture and system design
└── README.md           # Project documentation and Quickstart
```
> *Note: The `data/debug` folder contains intermediate `.txt` extractions. These are generated during ingestion to provide transparency into the OCR/Extraction process.*

