from pydantic import BaseModel, EmailStr
from datetime import datetime

# This file defines the "shapes" of data that travel through our API.
# Unlike models.py (which defines the actual database table),
# schemas define what's allowed IN a request and what's sent OUT in a response.

# We need three different shapes for a User:

# 1. UserCreate — what a signup request looks like.
#    A new user sends: username, email, and a plain password
#    (NOT hashed yet — hashing happens on the server, not the client)

# 2. UserResponse — what we send back to the frontend.
#    Should include id, username, email, created_at —
#    but NEVER the password, hashed or not.

# 3. UserLogin — what a login request looks like.
#    Just email and password — nothing else needed to log in.

# We also need shapes for journal entries:

# 4. JournalEntryCreate — what a request to add a journal entry looks like.
#    Just the content — milestone_id comes from the URL, not the body.

# 5. JournalEntryResponse — what we send back after creating/fetching
#    a journal entry. Includes id, content, milestone_id, created_at.


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class JournalEntryCreate(BaseModel):
    content: str


class JournalEntryResponse(BaseModel):
    id: int
    content: str
    milestone_id: int
    created_at: datetime

    class Config:
        from_attributes = True


"""
schemas.py's role in the project:
Defines what data is allowed in and out of the API for user signup,
login, profile responses, and journal entries.

Core idea:
Separates the public-facing shape of data (what the frontend sends and
receives) from the internal database shape (models/*.py). This
distinction matters most for security — UserResponse deliberately
excludes the password field entirely, so it can never accidentally
leak out through the API, even though the database itself stores it.
"""