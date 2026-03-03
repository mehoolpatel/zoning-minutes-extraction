from typing import List, Dict, Any
from app.core.schemas import DocumentRequest, DocumentChunk, DocumentMetadata

class DocumentChunker:
    def __init__(self, chunk_size: int = 1):                
        # 1 = One page per chunk
        # 999 = Whole Document approach (combine all pages)
        self.chunk_size = chunk_size                

    def chunk(self, documents: List[Dict[str, Any]]) -> List[DocumentChunk]:
        chunks = []
        for doc in documents:
            # 1. Use 'document_id' instead of 'id'
            source_id = doc.get("document_id", "unknown") 
            
            # 2. Extract text from 'text' key instead of 'content'
            all_pages = [
                page.get("text", "") 
                for page in doc["pages"]
            ]
            
            if self.chunk_size >= len(all_pages):
                full_content = "\n\n".join(all_pages)
                chunks.append(DocumentChunk(
                    content=full_content,                
                    # 1. Use source_id
                    metadata=DocumentMetadata(source_id=source_id, page_number=-1)
                ))
            else:
                for i in range(0, len(all_pages), self.chunk_size):
                    chunk_content = "\n\n".join(all_pages[i:i+self.chunk_size])
                    chunks.append(DocumentChunk(
                        content=chunk_content,
                        # 1. Use source_id
                        metadata=DocumentMetadata(source_id=source_id, page_number=i)
                    ))
        return chunks
