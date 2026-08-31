"""
routers/dreams.py

Defines the API endpoints for creating dreams, generating their
AI roadmap, and fetching dream/milestone data.

Endpoints:
    POST /dreams                             -> create a new dream
    POST /dreams/{dream_id}/generate-roadmap  -> generate milestones via LLM
    GET  /dreams                             -> list the current user's dreams
    GET  /dreams/{dream_id}                  -> fetch one dream + its milestones

Every endpoint requires authentication via get_current_user, and every
lookup by dream_id checks that the dream actually belongs to the
requesting user — a dream_id alone is never enough to access or modify
data that isn't yours (see FR-DREAM-07 in the SRS).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models.user import User
from models.dream import Dream
from schemas import DreamCreate, DreamResponse
from crud import create_dream, get_dream_by_id, get_dreams_by_user, save_milestones
from utils.llm_client import generate_roadmap, LLMGenerationError

router = APIRouter(prefix="/dreams", tags=["dreams"])


def _get_owned_dream_or_404(db: Session, dream_id: int, current_user: User) -> Dream:
    """
    Shared ownership check: fetches a dream by id and confirms it
    belongs to the requesting user. Raises 404 (not 403) if it
    doesn't belong to them or doesn't exist at all — this avoids
    leaking whether a given dream_id exists for someone else.
    """
    dream = get_dream_by_id(db, dream_id)
    if not dream or dream.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dream not found")
    return dream


@router.post("", response_model=DreamResponse, status_code=status.HTTP_201_CREATED)
def create_new_dream(
    dream: DreamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_dream(db, user_id=current_user.id, dream_data=dream)


@router.post("/{dream_id}/generate-roadmap", response_model=DreamResponse)
def generate_dream_roadmap(
    dream_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dream = _get_owned_dream_or_404(db, dream_id, current_user)

    try:
        milestones_data = generate_roadmap(dream.title, dream.description or "")
    except LLMGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Roadmap generation failed: {exc}",
        )

    save_milestones(db, dream_id=dream.id, milestones_data=milestones_data)
    db.refresh(dream)
    return dream


@router.get("", response_model=list[DreamResponse])
def list_my_dreams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_dreams_by_user(db, user_id=current_user.id)


@router.get("/{dream_id}", response_model=DreamResponse)
def get_dream(
    dream_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_owned_dream_or_404(db, dream_id, current_user)