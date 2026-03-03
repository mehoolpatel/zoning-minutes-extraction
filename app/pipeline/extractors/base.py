from abc import ABC, abstractmethod
from typing import List
from app.core.schemas import DocumentChunk, ExtractionResult

class BaseExtractor(ABC):
    """Abstract base class for extractors."""

    @abstractmethod
    def extract(self, chunks: List[DocumentChunk]) -> List[ExtractionResult]:
        """
        Transform DocumentChunk(s) into ExtractionResult(s).
        """
        pass
