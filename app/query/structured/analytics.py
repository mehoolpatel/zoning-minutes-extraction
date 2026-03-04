# app/query/structured/analytics.py
from sqlalchemy.orm import Session
from sqlalchemy import func, asc, text
from datetime import datetime, date
from typing import Optional, List
from app.models import structured as models
from app.core.schemas import VoteStatus  # Enum for vote status

def query_members(db: Session, member_name: Optional[str] = None, limit: int = 50):
    query = (
        db.query(
            models.Member.id,
            models.Member.name,
            func.min(models.DocumentModel.meeting_date).label("first_seen"),
            func.max(models.DocumentModel.meeting_date).label("last_seen"),
        )
        .join(models.MemberVote, models.Member.id == models.MemberVote.member_id)
        .join(models.MeetingItem, models.MemberVote.item_id == models.MeetingItem.id)
        .join(models.DocumentModel, models.MeetingItem.document_id == models.DocumentModel.id)
        .group_by(models.Member.id)
        .order_by(models.Member.name)
    )

    if member_name:
        query = query.filter(models.Member.name.contains(member_name))

    return query.limit(limit).all()

def query_votes(
    db: Session,
    member_id: Optional[int] = None,
    item_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
):
    """
    Return a list of DetailedVote ORM objects, optionally filtered by member,
    item_type, and date range. Sorted by most recent meeting_date first.
    """
    query = db.query(models.DetailedVote)

    # Filter by member_id
    if member_id:
        query = query.filter(models.DetailedVote.member_id == member_id)
    
    # Filter by item_type
    if item_type:
        query = query.filter(models.DetailedVote.item_type == item_type)

    # Filter by start_date
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(models.DetailedVote.meeting_date >= start)
        except ValueError:
            raise ValueError("start_date must be in YYYY-MM-DD format")

    # Filter by end_date
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(models.DetailedVote.meeting_date <= end)
        except ValueError:
            raise ValueError("end_date must be in YYYY-MM-DD format")

    # Sort by most recent first and apply limit
    return query.order_by(models.DetailedVote.meeting_date.desc()).limit(limit).all()


def _meeting_item_summary_query(db: Session):
    """
    Base query returning meeting item summary fields with vote counts.
    Uses count().filter() for efficiency and the VoteStatus Enum for accuracy.
    Does NOT filter by item yet.
    """
    return (
        db.query(
            models.MeetingItem.id.label("item_id"),
            models.MeetingItem.item_type,
            models.MeetingItem.item_name,
            models.DocumentModel.meeting_date,
            models.MeetingItem.action,

            # VOTE TOTAL (Yes + No + Abstain) - don't count Absent
            func.count(models.MemberVote.id)
                .filter(models.MemberVote.status.in_([
                    VoteStatus.YES.value, 
                    VoteStatus.NO.value, 
                    VoteStatus.ABSTAIN.value
                ]))
                .label("vote_count"),

            # Yes
            func.count(models.MemberVote.id)
                .filter(models.MemberVote.status == VoteStatus.YES.value)
                .label("yes_votes"),
                
            # No
            func.count(models.MemberVote.id)
                .filter(models.MemberVote.status == VoteStatus.NO.value)
                .label("no_votes"),

            # Abstain
            func.count(models.MemberVote.id)
                .filter(models.MemberVote.status == VoteStatus.ABSTAIN.value)
                .label("abstain_votes"),

            # Absent
            func.count(models.MemberVote.id)
                .filter(models.MemberVote.status == VoteStatus.ABSENT.value)
                .label("absent_count"),
        )
        .join(models.DocumentModel, models.MeetingItem.document_id == models.DocumentModel.id)
        .outerjoin(models.MemberVote, models.MemberVote.item_id == models.MeetingItem.id)
        .group_by(
            models.MeetingItem.id,
            models.DocumentModel.meeting_date,
            models.MeetingItem.action
        )
    )


def query_meeting_items(
    db: Session,
    item_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
):
    """
    Return a list of meeting items with summary counts.
    Optional filtering by item_type and date range.
    """
    query = _meeting_item_summary_query(db)

    if item_type:
        query = query.filter(models.MeetingItem.item_type == item_type)

    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        query = query.filter(models.DocumentModel.meeting_date >= start)

    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        query = query.filter(models.DocumentModel.meeting_date <= end)

    #return query.order_by(models.DocumentModel.meeting_date.desc()).limit(limit).all()
    return query.order_by(models.DocumentModel.meeting_date.desc()).limit(limit).all()

def query_meeting_item_detail(db: Session, item_id: int):
    """
    Returns a single meeting item summary with individual votes.
    Supports optional CASE fields on MeetingItem.
    """

    # ---- 1. Fetch summary row with CASE details ----
    item_summary = (
        db.query(
            models.MeetingItem.id.label("item_id"),
            models.MeetingItem.item_type,
            models.MeetingItem.item_name,
            models.DocumentModel.meeting_date,
            models.MeetingItem.action,

            # Optional CASE fields
            models.MeetingItem.applicant,
            models.MeetingItem.owner,
            models.MeetingItem.contact,
            models.MeetingItem.phone_number,
            models.MeetingItem.zoning,
            models.MeetingItem.location,
            models.MeetingItem.map_number,
            models.MeetingItem.variance_requested,
            models.MeetingItem.commission_district,
            models.MeetingItem.motion_by,
            models.MeetingItem.seconded_by,

            # Vote counts
            func.count(models.MemberVote.id)
                .filter(models.MemberVote.status.in_([
                    VoteStatus.YES.value,
                    VoteStatus.NO.value,
                    VoteStatus.ABSTAIN.value,
                ])).label("vote_count"),

            func.count(models.MemberVote.id)
                .filter(models.MemberVote.status == VoteStatus.YES.value)
                .label("yes_votes"),

            func.count(models.MemberVote.id)
                .filter(models.MemberVote.status == VoteStatus.NO.value)
                .label("no_votes"),

            func.count(models.MemberVote.id)
                .filter(models.MemberVote.status == VoteStatus.ABSTAIN.value)
                .label("abstain_votes"),

            func.count(models.MemberVote.id)
                .filter(models.MemberVote.status == VoteStatus.ABSENT.value)
                .label("absent_count"),
        )
        .join(models.DocumentModel, models.MeetingItem.document_id == models.DocumentModel.id)
        .outerjoin(models.MemberVote, models.MemberVote.item_id == models.MeetingItem.id)
        .filter(models.MeetingItem.id == item_id)
        .group_by(
            models.MeetingItem.id,
            models.MeetingItem.item_type,
            models.MeetingItem.item_name,
            models.DocumentModel.meeting_date,
            models.MeetingItem.action,
            models.MeetingItem.applicant,
            models.MeetingItem.owner,
            models.MeetingItem.contact,
            models.MeetingItem.phone_number,
            models.MeetingItem.zoning,
            models.MeetingItem.location,
            models.MeetingItem.map_number,
            models.MeetingItem.variance_requested,
            models.MeetingItem.commission_district,
            models.MeetingItem.motion_by,
            models.MeetingItem.seconded_by,
        )
        .first()
    )

    if not item_summary:
        return None

    # ---- 2. Fetch individual votes ----
    votes = (
        db.query(
            models.MemberVote.member_id,
            models.Member.name.label("member_name"),
            models.MemberVote.status.label("vote_cast"),
            models.MeetingItem.id.label("item_id"),
            models.MeetingItem.item_type,
            models.MeetingItem.item_name,
            models.DocumentModel.meeting_date,
        )
        .join(models.Member, models.MemberVote.member_id == models.Member.id)
        .join(models.MeetingItem, models.MemberVote.item_id == models.MeetingItem.id)
        .join(models.DocumentModel, models.MeetingItem.document_id == models.DocumentModel.id)
        .filter(models.MeetingItem.id == item_id)
        .order_by(models.Member.name.asc())
        .all()
    )

    return item_summary, votes

def query_member_statistics(db: Session, member_id: int):
    """
    Calculates aggregate statistics for a specific board member.
    """
    # Get Member basic info and tenure
    member_info = db.query(
        models.Member.id,
        models.Member.name,
        func.min(models.DocumentModel.meeting_date).label("first_seen"),
        func.max(models.DocumentModel.meeting_date).label("last_seen")
    ).join(models.MemberVote, models.Member.id == models.MemberVote.member_id) \
     .join(models.MeetingItem, models.MemberVote.item_id == models.MeetingItem.id) \
     .join(models.DocumentModel, models.MeetingItem.document_id == models.DocumentModel.id) \
     .filter(models.Member.id == member_id) \
     .group_by(models.Member.id).first()

    if not member_info:
        return None

    # Get Voting Totals
    vote_stats = db.query(
        func.count(models.MemberVote.id).label("total_votes"),
        func.count(models.MemberVote.id).filter(models.MemberVote.status == VoteStatus.YES.value).label("yes_votes"),
        func.count(models.MemberVote.id).filter(models.MemberVote.status == VoteStatus.NO.value).label("no_votes"),
        func.count(models.MemberVote.id).filter(models.MemberVote.status == VoteStatus.ABSTAIN.value).label("abstain_votes"),
        func.count(models.MemberVote.id).filter(models.MemberVote.status == VoteStatus.ABSENT.value).label("absent_votes")
    ).filter(models.MemberVote.member_id == member_id).first()

    # Combine into the nested structure the API expects
    return {
        "member_id": member_info.id,
        "member_name": member_info.name,
        "first_seen": member_info.first_seen,
        "last_seen": member_info.last_seen,
        "vote_summary": {  # Nesting this fixes the KeyError
            "total_votes": vote_stats.total_votes or 0,
            "yes_votes": vote_stats.yes_votes or 0,
            "no_votes": vote_stats.no_votes or 0,
            "abstain_votes": vote_stats.abstain_votes or 0,
            "absent_votes": vote_stats.absent_votes or 0
        }
    }