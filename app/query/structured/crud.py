from sqlalchemy.orm import Session
from app.models import structured as models
from app.core import schemas
from datetime import datetime 
import re
import logging

logger = logging.getLogger(__name__)

def clean_item_description(item_type: str, description: str) -> str:
    """Cleans up inconsistencies in item descriptions."""
    if not description:
        return description

    if item_type == "CASE":
        # Remove prefixes like "Case Number: " or "Case No: "
        clean_desc = re.sub(r'^(Case\s*(Number|No)?:\s*)', '', description, flags=re.IGNORECASE)
        return clean_desc.strip()
    
    #if item_type == "MINUTES":
    #    # Standardize "Approval of Minutes: [Date]" to just "Approval of Minutes"
    #    if "Approval of Minutes" in description:
    #        return "Approval of Minutes"
            
    return description

def get_or_create_document(db: Session, doc_id: str, meeting_date: str = None):
    parsed_date = None
    if meeting_date:
        parsed_date = datetime.strptime(meeting_date, "%Y-%m-%d").date()
    doc = db.query(models.DocumentModel).filter(models.DocumentModel.id == doc_id).first()
    if not doc:
        doc = models.DocumentModel(id=doc_id, meeting_date=parsed_date)
        db.add(doc)
        db.commit()
        db.refresh(doc)
    logger.info(f"[DOCUMENT CREATED] id={doc_id}, meeting_date={parsed_date}")
    return doc

def get_or_create_member(db: Session, name: str):
    # Members table still acts as the directory
    member = db.query(models.Member).filter(models.Member.name == name).first()
    if not member:
        member = models.Member(name=name)
        db.add(member)
        db.commit()
        db.refresh(member)
    return member

def ingest_extraction_result(db: Session, result: schemas.ExtractionResult):
    # 1. Ensure Document exists
    logger.info(f"[INGEST EXTRACT RESULT] document_id={result.document_id} meeting_date={result.meeting_date}")
    doc = get_or_create_document(db, result.document_id, result.meeting_date)
    
    for item_data in result.items:
        
        item_data.item_name = clean_item_description(item_data.item_type, item_data.item_name)
        
        # Create/Update Meeting Item
        # We need a unique constraint (e.g., document_id + item_name) to upsert
        item = db.query(models.MeetingItem).filter(
            models.MeetingItem.document_id == doc.id,
            models.MeetingItem.item_name == item_data.item_name
        ).first()

        if not item:
            item = models.MeetingItem(document_id=doc.id, **item_data.model_dump(exclude={'votes'}))
            db.add(item)
            db.commit()
            db.refresh(item)
        else:
            # Update existing item fields
            for key, value in item_data.model_dump(exclude={'votes'}).items():
                setattr(item, key, value)
            db.commit()

        # Handle Votes
        for vote_data in item_data.votes:
            # Retrieve or create the member to get their database ID
            member = get_or_create_member(db, vote_data.member_name)
           
            # Upsert Vote for this specific item
            existing_vote = db.query(models.MemberVote).filter(
                models.MemberVote.item_id == item.id,
                models.MemberVote.member_id == member.id 
            ).first()

            if existing_vote:
                existing_vote.status = vote_data.status
                existing_vote.raw_status = vote_data.raw_status
            else:
                db.add(models.MemberVote(
                    item_id=item.id,
                    member_id=member.id, 
                    status=vote_data.status,
                    raw_status=vote_data.raw_status
                ))
    
    db.commit()