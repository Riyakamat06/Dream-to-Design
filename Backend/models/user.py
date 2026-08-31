from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


# This file defines the User table — every student who signs up
# gets one row here. Other tables (like Dream) link back to this
# table using a user_id foreign key.

class User(Base):
    __tablename__ = "users"

    # a unique id
    id = Column(Integer, primary_key=True, index=True)

    # a username
    username = Column(String, nullable=False)

    # an email (must be unique — no two users share one)
    email = Column(String, unique=True, nullable=False)

    # a hashed password (never store the real password!)
    hashed_password = Column(String, nullable=False)

    # when they signed up
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # a user can have many dreams
    dreams = relationship("Dream", back_populates="user")
    # JournalEntry — a student's reflection tied to a specific milestone.
# Remember the decision from earlier: journal entries attach to a
# milestone, not directly to a dream or user (matches FR-5 in the SRS).

# A JournalEntry needs:
# - a unique id
# - the actual reflection text
# - which milestone it belongs to (a foreign key)
# - when it was written
class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=False)

    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    milestone = relationship("Milestone", back_populates="journal_entries")
   """
models/user.py's role in the project:
Defines the User table (student accounts) and the JournalEntry table
(reflections a student writes, tied to a specific milestone).

Core idea:
User follows the same relationship pattern as dream.py (a ForeignKey
column paired with a relationship() line) to complete the two-way
link between User and Dream. JournalEntry links back to Milestone
(owned by dream.py) the same way — proving SQLAlchemy resolves
foreign keys by table name at runtime, not by which file imports
which, so two files written by different people can reference each
other without ever importing one another directly.
"""