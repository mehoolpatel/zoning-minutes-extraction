# app/schemas/analytics.py
# Purpose: Pydantic models for API RESPONSES.
# These models define the JSON structure sent to the frontend
# for analytical endpoints (listing votes, member summaries, etc.).

from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import date

class VoteSummary(BaseModel):
    member_id: int
    member_name: str
    votes_summary: Dict[str, int] # e.g., {"Yes": 10, "No": 2}
    consensus_rate: float
    
    class Config:
        from_attributes = True

class ApprovalSummary(BaseModel):
    summary: Dict[str, int] # e.g., {"Approved": 10, "Denied": 2}
    
    class Config:
        from_attributes = True

class VoteRow(BaseModel):
    member_name: str
    member_id: int
    item_type: str
    item_id: int                    # reference to the meeting item row
    description: str
    vote_cast: str
    meeting_date: date  

class MeetingItemRow(BaseModel):
    item_id: int
    item_type: str
    item_name: Optional[str]
    meeting_date: date              
    vote_count: int
    yes_votes: int
    no_votes: int
    abstain_votes: int  
    absent_count: int
    action: Optional[str]

    class Config:
        from_attributes = True

class MeetingItemDetailRow(MeetingItemRow):
    # optional detailed fields for CASE items
    applicant: Optional[str] = None
    owner: Optional[str] = None
    contact: Optional[str] = None
    phone_number: Optional[str] = None
    zoning: Optional[str] = None
    location: Optional[str] = None
    map_number: Optional[str] = None
    variance_requested: Optional[str] = None
    commission_district: Optional[str] = None
    motion_by: Optional[str] = None
    seconded_by: Optional[str] = None
    votes: List[VoteRow] = []

class MemberStatistics(BaseModel):
    member_id: int
    member_name: str
    first_seen: Optional[date] 
    last_seen: Optional[date] 
    vote_summary: Dict[str, int]