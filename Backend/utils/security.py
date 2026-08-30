from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from config import get_settings

# This file handles two separate jobs:
#
# 1. Password security — turning a plain password into a scrambled
#    (hashed) version to store, and checking a login attempt against
#    that stored hash without ever storing the real password.
#
# 2. Login tokens (JWT) — after a successful login, we give the user
#    a signed token. That token proves who they are on every future
#    request, without them having to re-enter their password each time.

# We need four functions:
# - hash_password(password) -> turns a plain password into a hash
# - verify_password(plain_password, hashed_password) -> checks login attempt
# - create_access_token(data) -> builds a signed JWT after successful login
# - decode_access_token(token) -> reads a JWT and confirms it's valid


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except jwt.JWTError:
        return None


"""
auth.py's role in the project:
Handles password security (hashing and verifying) and login tokens (JWT
creation and decoding) — the two building blocks every login-protected
endpoint depends on.

Core idea:
Passwords are never stored or compared directly — only their hashed form,
using bcrypt's one-way scrambling. Login tokens are signed with a secret
key from .env, so the server can verify a token wasn't forged without
storing session state anywhere — decode_access_token is what
dependencies.py will use to identify the logged-in user on every request.
"""