import os
import json
import logging
from typing import List, Dict, Any
from app.core.schemas import DocumentChunk, ExtractionResult, VoteStatus, MemberVote
from .base import BaseExtractor

logger = logging.getLogger(__name__)
class MockExtractor(BaseExtractor):
    """Simplified extractor for demonstration purposes."""

    def _normalize_vote(self, raw_vote: str) -> VoteStatus:
        if not raw_vote:
            return VoteStatus.UNKNOWN
            
        clean = raw_vote.strip().lower()

        # Strong mappings
        if "yes" in clean or "aye" in clean or "approved" in clean: 
            return VoteStatus.YES
        if "no" in clean or "nay" in clean or "denied" in clean: 
            return VoteStatus.NO
        
        # Domain-specific edge cases
        if "absent" in clean or "not present" in clean: 
            return VoteStatus.ABSENT
        if "out" in clean and "room" in clean: 
            return VoteStatus.OUT_OF_ROOM
        if "recus" in clean:
            return VoteStatus.RECUSED
            
        return VoteStatus.UNKNOWN

    def _call_llm(self, content: str) -> List[Dict[str, str]]:
        return [
            {
                "name": "John Doe",
                "vote": "Yes"
            }
        ]

    def extract(self, chunks: List[DocumentChunk]) -> List[ExtractionResult]:
        results = []
        for chunk in chunks:
            raw_votes = self._call_llm(chunk.content)
            
            # Map raw data to Pydantic models
            normalized_votes = [
                MemberVote(
                    member_name=mv["name"],
                    status=self._normalize_vote(mv["vote"]),
                    raw_status=mv["vote"]
                )
                for mv in raw_votes
            ]
            
            results.append(
                ExtractionResult(
                    document_id=chunk.metadata.source_id,
                    page_number=chunk.metadata.page_number,
                    votes=normalized_votes
                )
            )
        return results