# app/models/structured.py
# Purpose: SQLAlchemy Models for DATABASE STORAGE.
# These classes define the database schema (tables and relationships)
# for SQLAlchemy ORM mapping.

from sqlalchemy import Table, Column, Integer, String, Date, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import registry, relationship
from app.core.db import Base, engine

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    first_seen = Column(Date)
    last_seen = Column(Date)

    # Relationships
    votes = relationship("MemberVote", back_populates="member", foreign_keys="[MemberVote.member_id]")
    # actions = relationship("Action", back_populates="actor")

class MemberVote(Base):
    __tablename__ = "member_votes"
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("meeting_items.id"))
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    # member_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    raw_status = Column(String, nullable=False)

    # Relationships
    item = relationship("MeetingItem", back_populates="votes")
    member = relationship("Member", back_populates="votes")

class DetailedVote(Base):
    __tablename__ = "detailed_votes"
    __table_args__ = {"info": {"is_view": True}}

    vote_id = Column(Integer, primary_key=True)
    vote_cast = Column(String)
    member_name = Column(String)
    member_id = Column(Integer)
    item_description = Column(String)
    item_type = Column(String)
    meeting_date = Column(Date)

class MeetingItem(Base):
    __tablename__ = "meeting_items"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"))
    item_type = Column(String, nullable=False)
    item_name = Column(String, nullable=False)
    page_number = Column(Integer)
    
    # Case-specific
    applicant = Column(String)
    owner = Column(String)
    contact = Column(String)
    phone_number = Column(String)
    zoning = Column(String)
    location = Column(String)
    map_number = Column(String)
    variance_requested = Column(String)
    commission_district = Column(String)
    
    # Common
    action = Column(String)
    motion_by = Column(String)
    seconded_by = Column(String)

    # Relationships
    document = relationship("DocumentModel", back_populates="items")
    votes = relationship("MemberVote", back_populates="item")

class DocumentModel(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True)
    meeting_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationship to items
    items = relationship("MeetingItem", back_populates="document")