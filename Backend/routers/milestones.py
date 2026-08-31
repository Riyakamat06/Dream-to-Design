from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
from models.user import User
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
router = APIRouter(prefix="/milestones", tags=["milestones"])
# Endpoints needed:
# - PATCH /milestones/{id}/complete -> mark a milestone as done
@router.patch("/{milestone_id}/complete")
def complete_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    milestone = get_milestone_by_id(db, milestone_id)
    if milestone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found",
        )

    updated_milestone = mark_milestone_complete(db, milestone)
    return {"id": updated_milestone.id, "is_completed": updated_milestone.is_completed}
# - POST /milestones/{id}/journal -> add a journal entry to a milestone
@router.post("/{milestone_id}/journal", response_model=JournalEntryResponse)
def add_journal_entry(
    milestone_id: int,
    entry: JournalEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    milestone = get_milestone_by_id(db, milestone_id)
    if milestone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found",
        )

    new_entry = create_journal_entry(db, milestone_id, entry)
    return new_entry

# - GET /milestones/{id}/journal -> fetch all journal entries for a milestone
@router.get("/{milestone_id}/journal", response_model=list[JournalEntryResponse])
def list_journal_entries(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    milestone = get_milestone_by_id(db, milestone_id)
    if milestone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found",
        )

    return get_journal_entries_for_milestone(db, milestone_id)

# All of these require a logged-in user (get_current_user) —
# though note: right now we don't yet check that the milestone
# actually belongs to that user's own dream. That's a real gap
# worth flagging to Riya, since milestone ownership traces through
# Dream.user_id, which her routers/dreams.py will also need.