from pydantic import BaseModel, EmailStr
from datetime import datetime
# This file defines the "shapes" of data that travel through our API.
# Unlike models.py (which defines the actual database table),
# schemas define what's allowed IN a request and what's sent OUT in a response.

# We need three different shapes for a User:

# 1. UserCreate — what a signup request looks like.
#    A new user sends: username, email, and a plain password
#    (NOT hashed yet — hashing happens on the server, not the client)
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
# 2. UserResponse — what we send back to the frontend.
#    Should include id, username, email, created_at —
#    but NEVER the password, hashed or not.
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

# 3. UserLogin — what a login request looks like.
#    Just email and password — nothing else needed to log in.+
class UserLogin(BaseModel):
    email: EmailStr
    password: str