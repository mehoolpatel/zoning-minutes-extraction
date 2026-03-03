from pathlib import Path
import os
import json
import logging
import pdfplumber
from app.core.schemas import DocumentChunk, DocumentMetadata

PDF_FOLDER = Path("data/pdfs")
DEBUG_DIR = "data/debug"
os.makedirs(DEBUG_DIR, exist_ok=True)

# Get the logger for this specific module
logger = logging.getLogger(__name__)

def load_documents(use_mock: bool = True, dump_pages: bool = False):
    """
    Loads documents for the ingestion pipeline.
    - If use_mock=True, load from mock JSON files
    - If use_mock=False, load real PDFs
    - If dump_pages=True, save extracted page text to disk for debugging
    """
    logger.info(f"Loading docs, use_mock={use_mock}, dump_pages={dump_pages}")

    if use_mock:
        return _load_mock_documents(dump_pages=dump_pages)
    else:
        return _load_real_documents(dump_pages=dump_pages)

def _load_mock_documents(dump_pages: bool = False):
    """
    Load mock OCR outputs from JSON files.
    Returns a list of documents, each with a 'pages' list.
    """
    docs = []
    test_dir = Path("data/mock_ocr_outputs")

    if not test_dir.exists():
        logger.warning(f"Directory {test_dir} not found.")
        return []

    for json_file in test_dir.glob("*.json"):
        try:
            file_data = json.loads(json_file.read_text(encoding="utf-8"))
            docs.append(file_data)
        except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse {json_file.name}: {e}")
                    continue # Skip broken files and keep going
        
    logger.info(f"Loaded {len(docs)} mock documents.")
    return docs


def _load_real_documents(dump_pages: bool = False):
    """
    Load all PDFs from data/pdfs, extract text per page, 
    and return in same structure as _load_mock_documents.

    Robustness checks:
        - Logs empty PDFs or PDFs with zero pages
        - Skips pages without text but still keeps a placeholder page to avoid chunker errors
        - Catches exceptions per PDF so one bad file doesn't halt the pipeline
        - Returns a consistent structure (even empty pages list) so chunker doesn't break
        - Info logs for how many PDFs and pages were loaded
    """
    if not PDF_FOLDER.exists():
        logger.warning(f"PDF folder {PDF_FOLDER} does not exist.")
        return []

    docs = []
    pdf_files = list(PDF_FOLDER.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDFs found in {PDF_FOLDER}.")
        return []

    for pdf_path in pdf_files:
        logger.info(f"Processing PDF: {pdf_path.name}")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if not pdf.pages:
                    logger.warning(f"PDF {pdf_path.name} has no pages.")
                    continue # skip this PDF

                pages = []
                for i, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text(layout=True)
                        if not text:
                            logger.debug(f"Page {i+1} of {pdf_path.name} is empty.")
                            text = ""  # safe default for empty page
                        pages.append({"page_number": i + 1, "text": text})
                        
                        # Debug: save each page to a separate txt file
                        if dump_pages:
                            debug_file = os.path.join(DEBUG_DIR, f"{pdf_path.stem}_page_{i+1}.txt")
                            try:
                                with open(debug_file, "w", encoding="utf-8") as f:
                                    f.write(text)
                            except Exception as e:
                                logger.error(f"Failed to write debug page {i+1} of {pdf_path.name}: {e}")

                    except Exception as e:
                        logger.error(f"Failed to extract page {i+1} of {pdf_path.name}: {e}")
                        pages.append({"page_number": i + 1, "text": ""})  # still include placeholder

                doc = {
                    "file_name": pdf_path.name,
                    "pages": pages,
                }
                docs.append(doc)
        except Exception as e:
            logger.error(f"Failed to process {pdf_path.name}: {e}")
            continue

    total_pages = sum(len(d['pages']) for d in docs)
    logger.info(f"Loaded {len(docs)} PDFs with {total_pages} total pages from {PDF_FOLDER}")
    return docs