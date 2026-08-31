from sqlalchemy.orm import Session
from models.user import User, JournalEntry
from models.dream import Dream, Milestone
from schemas import UserCreate, JournalEntryCreate
from utils.security import hash_password

# This file holds reusable database query functions — the actual
# logic for reading/writing to the database, kept separate from
# the API endpoints themselves (routers/auth.py, routers/milestones.py).

# Why separate this from the router?
# - Keeps routers focused on HTTP concerns (status codes, request/response shapes)
# - Lets the same query logic be reused across multiple endpoints
#   (e.g. both signup and login need to look up a user by email)

# Functions needed for users:
# - get_user_by_email(db, email) -> finds a user, or None if not found
# - create_user(db, user) -> saves a new user to the database

# Functions needed for milestones and journal entries:
# - get_milestone_by_id(db, milestone_id) -> finds a milestone, or None
# - mark_milestone_complete(db, milestone) -> sets is_completed=True, saves
# - create_journal_entry(db, milestone_id, entry) -> saves a new journal entry
# - get_journal_entries_for_milestone(db, milestone_id) -> fetches all entries


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate) -> User:
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_milestone_by_id(db: Session, milestone_id: int) -> Milestone | None:
    return db.query(Milestone).filter(Milestone.id == milestone_id).first()


def mark_milestone_complete(db: Session, milestone: Milestone) -> Milestone:
    milestone.is_completed = True
    db.commit()
    db.refresh(milestone)
    return milestone


def create_journal_entry(db: Session, milestone_id: int, entry: JournalEntryCreate) -> JournalEntry:
    new_entry = JournalEntry(
        milestone_id=milestone_id,
        content=entry.content,
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry


def get_journal_entries_for_milestone(db: Session, milestone_id: int) -> list[JournalEntry]:
    return db.query(JournalEntry).filter(JournalEntry.milestone_id == milestone_id).all()

# --- Dream & Milestone CRUD  ---

def create_dream(db: Session, user_id: int, dream_data) -> Dream:
    new_dream = Dream(
        user_id=user_id,
        title=dream_data.title,
        description=dream_data.description,
        category=dream_data.category,
        target_date=dream_data.target_date,
    )
    db.add(new_dream)
    db.commit()
    db.refresh(new_dream)
    return new_dream


def get_dream_by_id(db: Session, dream_id: int) -> Dream | None:
    return db.query(Dream).filter(Dream.id == dream_id).first()


def get_dreams_by_user(db: Session, user_id: int) -> list[Dream]:
    return db.query(Dream).filter(Dream.user_id == user_id).all()


def save_milestones(db: Session, dream_id: int, milestones_data: list[dict]) -> list[Milestone]:
    milestone_objects = [
        Milestone(
            dream_id=dream_id,
            title=m["title"],
            description=m.get("description"),
            order=m["order"],
            estimated_effort=m.get("estimated_effort"),
        )
        for m in milestones_data
    ]
    db.add_all(milestone_objects)
    db.commit()
    for m in milestone_objects:
        db.refresh(m)
    return milestone_objects
"""
crud.py's role in the project:
Holds reusable database query and write functions for users,
milestones, and journal entries, kept separate from the API
endpoints in routers/auth.py and routers/milestones.py.

Core idea:
Endpoints handle HTTP concerns (status codes, request validation);
crud.py handles the actual database logic. This means query logic
like get_user_by_email() or get_milestone_by_id() lives in exactly
one place, reused across multiple endpoints instead of duplicated.
"""