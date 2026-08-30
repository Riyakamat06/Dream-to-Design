from sqlalchemy.orm import Session
from models.user import User
from schemas import UserCreate
from utils.security import hash_password

# This file holds reusable database query functions — the actual
# logic for reading/writing to the database, kept separate from
# the API endpoints themselves (routers/users.py).

# Why separate this from the router?
# - Keeps routers focused on HTTP concerns (status codes, request/response shapes)
# - Lets the same query logic be reused across multiple endpoints
#   (e.g. both signup and login need to look up a user by email)

# Functions needed for users:
# - get_user_by_email(db, email) -> finds a user, or None if not found
# - create_user(db, user) -> saves a new user to the database


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


"""
crud.py's role in the project:
Holds reusable database query and write functions for users, kept
separate from the API endpoints in routers/users.py.

Core idea:
Endpoints handle HTTP concerns (status codes, request validation);
crud.py handles the actual database logic. This means the same
get_user_by_email() logic used in both signup (checking for
duplicates) and login (looking up credentials) lives in exactly
one place instead of being duplicated across the router.
"""