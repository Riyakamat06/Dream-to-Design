from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from auth import decode_access_token
from models.user import User

# This file provides get_current_user() — a function that every
# protected endpoint (e.g. "create a dream", "view my profile")
# will use to check: is there a valid logged-in user making this request?

# How it works:
# 1. FastAPI automatically extracts the token from the request's
#    Authorization header (sent as "Bearer <token>")
# 2. We decode that token using decode_access_token() from auth.py
# 3. If the token is invalid or missing -> reject the request (401 error)
# 4. If valid -> look up the actual User in the database using the
#    email/id stored inside the token, and return that User object


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


"""
dependencies.py's role in the project:
Provides get_current_user() — the single function every protected
endpoint depends on to identify who's making a request.

Core idea:
Uses FastAPI's dependency injection (Depends) to automatically extract
and validate a login token from every incoming request, then looks up
the real User row it belongs to. If the token is missing, invalid, or
doesn't match a real user, the request is rejected with a 401 error
before the endpoint's actual logic ever runs. This is what makes routes
like "create a dream" or "view my profile" possible without each one
rewriting the same authentication check.
"""