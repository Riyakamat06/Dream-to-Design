from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas import UserCreate, UserResponse, UserLogin
from auth import hash_password, verify_password, create_access_token

# This file defines the actual API endpoints for user accounts:
# - POST /users/signup -> create a new account
# - POST /users/login -> verify credentials, return a login token

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


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


"""
routers/users.py's role in the project:
Defines the actual signup and login API endpoints — the entry points
the frontend will call to create an account and authenticate.

Core idea:
Ties together everything built today: schemas validate incoming data,
auth.py handles password hashing and token creation, and database.py
provides the session. response_model=UserResponse on signup ensures
the password can never leak into the API response, even by accident.
"""