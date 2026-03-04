# app/core/schemas.py
# Purpose: Pydantic models for DATA INGESTION and LLM OUTPUT.
# These models define how data is structured when extracted from PDFs
# and passed through the ingestion pipeline before being saved to the DB.

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class VoteStatus(str, Enum):
    YES = "Yes"
    NO = "No"
    ABSTAIN = "Abstain"
    ABSENT = "Absent"
    OUT_OF_ROOM = "Out of Room"
    RECUSED = "Recused"
    UNKNOWN = "Unknown"             # catch-all

class MemberVote(BaseModel):
    member_name: str
    status: VoteStatus
    raw_status: str                 # exactly what the LLM returned

class ItemType(str, Enum):
    CASE = "CASE"
    AGENDA = "AGENDA"
    MINUTES = "MINUTES"
    ADJOURNMENT = "ADJOURNMENT"
    OTHER = "OTHER"                 # catch-all for unexpected types

class MeetingItem(BaseModel):
    item_type: ItemType
    item_name: str # Case number (e.g., VAR2025-00004) or Item name (e.g., "Approval of Agenda")

    page_number: Optional[int] = None

    # Specific to CASE, Optional for others
    applicant: Optional[str] = None
    owner: Optional[str] = None
    contact: Optional[str] = None
    phone_number: Optional[str] = None
    zoning: Optional[str] = None
    location: Optional[str] = None
    map_number: Optional[str] = None
    variance_requested: Optional[str] = None
    commission_district: Optional[str] = None
    
    # Generic fields for all item types
    action: Optional[str] = None
    motion_by: Optional[str] = None
    seconded_by: Optional[str] = None
    votes: List[MemberVote] = Field(default_factory=list)

    class Config:
            json_schema_extra = {
                "example": {
                    "item_type": "CASE",
                    "item_name": "ZVR2025-00027",
                    "meeting_date": "2025-04-08",
                    "applicant": "Hikmat Mammadov",
                    "location": "4495 Sugarloaf Parkway",
                    "zoning": "R-100",
                    "variance_requested": "Exceed maximum fence height",
                    "action": "Approved with Conditions",
                    "motion_by": "Bess Walthour",
                    "seconded_by": "Rich Edinger",
                    "votes": [
                        {
                            "member_name": "Bess Walthour", 
                            "member_id": 3,
                            "vote_cast": "Yes",
                            "meeting_date": "2025-04-08"
                        },
                        {
                            "member_name": "Rich Edinger", 
                            "member_id": 2,
                            "vote_cast": "Yes",
                            "meeting_date": "2025-04-08"
                        }
                    ]
                }
            }

class ExtractionResult(BaseModel):
    """
    Represents the structured extraction from a full document or chunk.
    """
    document_id: str
    meeting_date: Optional[str] = None
    items: List[MeetingItem] = Field(default_factory=list)

class DocumentRequest(BaseModel):
    """Represents a full loaded document (e.g., a PDF) and its content."""
    id: str = Field(..., description="Unique identifier for the document")
    title: Optional[str] = None
    # Map page number to page content text
    pages: Dict[int, str] = Field(default_factory=dict, description="Dictionary mapping page number to text")

class DocumentMetadata(BaseModel):
    """Basic tracking for data lineage."""
    source_id: str
    page_number: Optional[int] = None
    # We use a list because one chunk might technically contain 
    # multiple mentions or actions
    extraction: Optional[List[ExtractionResult]] = Field(default_factory=list)

class DocumentChunk(BaseModel):
    """The exchange format for the ingestion pipeline."""
    content: str
    metadata: DocumentMetadata
