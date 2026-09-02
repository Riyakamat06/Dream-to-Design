from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
from models.user import User
from models.dream import Milestone
from schemas import JournalEntryCreate, JournalEntryResponse
from crud import (
    get_milestone_by_id,
    mark_milestone_complete,
    create_journal_entry,
    get_journal_entries_for_milestone,
)

# This file defines endpoints for working with milestones and
# journal entries — the day-to-day tracking features once a
# dream's roadmap already exists.

# Endpoints needed:
# - PATCH /milestones/{id}/complete -> mark a milestone as done
# - POST /milestones/{id}/journal -> add a journal entry to a milestone
# - GET /milestones/{id}/journal -> fetch all journal entries for a milestone

# Every endpoint requires authentication via get_current_user, and every
# lookup by milestone_id checks that the milestone's dream actually
# belongs to the requesting user — same ownership pattern as
# routers/dreams.py's _get_owned_dream_or_404, adapted here since a
# Milestone's ownership traces through milestone.dream.user_id.


router = APIRouter(prefix="/milestones", tags=["milestones"])


def _get_owned_milestone_or_404(db: Session, milestone_id: int, current_user: User) -> Milestone:
    """
    Shared ownership check: fetches a milestone by id and confirms
    it belongs to a dream owned by the requesting user. Raises 404
    (not 403) whether the milestone doesn't exist or belongs to
    someone else — same reasoning as Riya's _get_owned_dream_or_404
    in routers/dreams.py.
    """
    milestone = get_milestone_by_id(db, milestone_id)
    if not milestone or milestone.dream.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")
    return milestone


@router.patch("/{milestone_id}/complete")
def complete_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    milestone = _get_owned_milestone_or_404(db, milestone_id, current_user)
    updated_milestone = mark_milestone_complete(db, milestone)
    return {"id": updated_milestone.id, "is_completed": updated_milestone.is_completed}


@router.post("/{milestone_id}/journal", response_model=JournalEntryResponse)
def add_journal_entry(
    milestone_id: int,
    entry: JournalEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    milestone = _get_owned_milestone_or_404(db, milestone_id, current_user)
    new_entry = create_journal_entry(db, milestone.id, entry)
    return new_entry


@router.get("/{milestone_id}/journal", response_model=list[JournalEntryResponse])
def list_journal_entries(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    milestone = _get_owned_milestone_or_404(db, milestone_id, current_user)
    return get_journal_entries_for_milestone(db, milestone.id)


"""
routers/milestones.py's role in the project:
Defines endpoints for marking milestones complete and managing
journal entries tied to them.

Core idea:
Every endpoint checks ownership via _get_owned_milestone_or_404,
which traces through milestone.dream.user_id to confirm the
requesting user actually owns the dream this milestone belongs to.
This closes the security gap flagged earlier — previously any
logged-in user could modify any milestone regardless of who it
belonged to. Mirrors the same 404-not-403 pattern Riya used in
routers/dreams.py, so an invalid milestone_id and someone else's
milestone are indistinguishable to an attacker.
"""