# app/api/v1/analytics.py
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from app.core.db import get_db
from app.query.structured import analytics as db_query
from app.schemas.analytics import VoteSummary, ApprovalSummary, VoteRow, MeetingItemRow, MeetingItemDetailRow, MemberStatistics

router = APIRouter()

# member directory listing
@router.get("/members", 
            summary="List Board Members", 
            description="Returns a directory of all board members identified in processed records, sorted by last name.")
def list_members(
    db: Session = Depends(get_db),
    member_name: Optional[str] = None,
    limit: Optional[int] = Query(50, ge=1, le=500)
):
    members_data = db_query.query_members(db, member_name, limit)
    
    # Unpack all 4 values returned by the query
    members_list = [
        {
            "id": member_id, 
            "name": member_name,
            "first_seen": first_seen, 
            "last_seen": last_seen
        }
        for member_id, member_name, first_seen, last_seen in members_data
    ]
    # Sort alphabetically by last name
    members_list = sorted(
        members_list,
        key=lambda x: x["name"].split()[-1].lower()
    )
    return members_list

# timeline (history) of votes
@router.get("/votes", 
            response_model=List[VoteRow],
            summary="Query Voting History",
            description="Retrieve a filterable timeline of individual votes cast across all meetings.")
def list_votes(
    db: Session = Depends(get_db),
    member_id: Optional[int] = None,
    item_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500)
):
    votes = db_query.query_votes(db, member_id, item_type, start_date, end_date, limit)
    return [
        VoteRow(
            member_name=v.member_name,
            member_id=v.member_id,
            item_type=v.item_type,
            item_id=v.vote_id,           # or MeetingItem id if you modify view
            description=v.item_description,
            vote_cast=v.vote_cast,
            meeting_date=str(v.meeting_date)
        )
        for v in votes
    ]

@router.get("/meeting-items", 
            response_model=List[MeetingItemRow],
            summary="List Voted Meeting Items",
            description="Retrieve all items brought to a vote, including zoning cases, agenda approvals, and administrative motions.")
def list_meeting_items(
    db: Session = Depends(get_db),
    item_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500)
):
    items = db_query.query_meeting_items(
        db=db,
        item_type=item_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )

    # Convert ORM rows / named tuples into Pydantic MeetingItemRow
    return [
        MeetingItemRow(
            item_id=row.item_id,
            item_type=row.item_type,
            item_name=row.item_name,
            meeting_date=row.meeting_date,      # keep as a Date object, Pydantic handles the rest
            vote_count=row.vote_count,
            yes_votes=row.yes_votes,
            no_votes=row.no_votes,
            abstain_votes=row.abstain_votes,
            absent_count=row.absent_count,
            action=row.action,
        )
        for row in items
    ]

@router.get("/meeting-items/{item_id}", 
            response_model=MeetingItemDetailRow,
            summary="Get Item Details",
            description="Retrieve full metadata for a specific zoning case, including petitioners, locations, and the full vote tally.")
def get_meeting_item(item_id: int, db: Session = Depends(get_db)):
    result = db_query.query_meeting_item_detail(db, item_id)
    if not result:
        raise HTTPException(status_code=404, detail="Meeting item not found")

    item_summary, votes_data = result

    # Convert votes to VoteRow
    votes_list = [
        VoteRow(
            member_name=v.member_name,
            member_id=v.member_id,
            item_type=v.item_type,
            item_id=v.item_id,
            description=v.item_name,        # optional, renamed to description
            vote_cast=v.vote_cast,
            meeting_date=v.meeting_date     # keep as a Date object, Pydantic handles the rest
        )
        for v in votes_data
    ]

    # Build MeetingItemDetailRow using all fields (including CASE extras)
    return MeetingItemDetailRow(
        item_id=item_summary.item_id,
        item_type=item_summary.item_type,
        item_name=item_summary.item_name,
        meeting_date=item_summary.meeting_date,
        vote_count=item_summary.vote_count,
        yes_votes=item_summary.yes_votes,
        no_votes=item_summary.no_votes,
        abstain_votes=item_summary.abstain_votes,
        absent_count=item_summary.absent_count,
        action=item_summary.action,

        # ---- CASE-specific optional fields ----
        applicant=getattr(item_summary, "applicant", None),
        owner=getattr(item_summary, "owner", None),
        contact=getattr(item_summary, "contact", None),
        phone_number=getattr(item_summary, "phone_number", None),
        zoning=getattr(item_summary, "zoning", None),
        location=getattr(item_summary, "location", None),
        map_number=getattr(item_summary, "map_number", None),
        variance_requested=getattr(item_summary, "variance_requested", None),
        commission_district=getattr(item_summary, "commission_district", None),
        motion_by=getattr(item_summary, "motion_by", None),
        seconded_by=getattr(item_summary, "seconded_by", None),

        # ---- votes list ----
        votes=votes_list
    )

@router.get("/members/{member_id}", 
            response_model=MemberStatistics,
            summary="Get Member Statistics",
            description="Returns aggregated vote counts (Yes/No/Abstain) and tenure dates for a specific member.")
def get_member_statistics(member_id: int, db: Session = Depends(get_db)):
    """
    Returns aggregated vote statistics and first/last seen dates for a specific member.
    """
    result = db_query.query_member_statistics(db, member_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Member not found")
    
    return MemberStatistics(
        member_id=result["member_id"],
        member_name=result["member_name"],
        first_seen=result["first_seen"],
        last_seen=result["last_seen"],
        vote_summary=result["vote_summary"]
    )
