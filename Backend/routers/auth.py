from dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas import UserCreate, UserResponse, UserLogin
from utils.security import verify_password, create_access_token
from crud import get_user_by_email, create_user

# This file defines the actual API endpoints for user accounts:
# - POST /users/signup -> create a new account
# - POST /users/login -> verify credentials, return a login token
# - GET /users/me -> return the logged-in user's own profile

# Signup flow:
# 1. Receive username, email, password (validated by UserCreate schema)
# 2. Check the email isn't already taken
# 3. Hash the password (never store it plain)
# 4. Save the new user to the database
# 5. Return the new user's public info (UserResponse — no password)

# Login flow:
# 1. Receive email, password (validated by UserLogin schema)
# 2. Look up the user by email
# 3. Verify the password matches the stored hash
# 4. If valid, create and return an access token
# 5. If invalid, reject with a 401 error

# /me flow:
# 1. Uses get_current_user to identify who's making the request
#    (requires a valid token in the Authorization header)
# 2. Returns that user's own profile — no lookup needed, since
#    get_current_user already found the exact right user


router = APIRouter(prefix="/users", tags=["auth"])


@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = create_user(db, user)
    return new_user


@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, credentials.email)

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


"""
routers/auth.py's role in the project:
Defines the actual signup, login, and current-user-profile API
endpoints — the entry points the frontend will call to create an
account, authenticate, and check who's logged in.

Core idea:
Ties together everything in the auth module: schemas validate
incoming data, crud.py handles database queries, utils/security.py
handles password hashing and token creation, and dependencies.py
identifies the logged-in user via get_current_user. response_model
on signup and /me ensures the password can never leak into an API
response, even by accident.
"""