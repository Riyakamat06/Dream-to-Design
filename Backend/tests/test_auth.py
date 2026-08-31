import uuid
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
# This file tests that signup and login actually work correctly,
# and that they properly reject bad attempts (not just the happy path).

# Tests needed:
# 1. test_signup_creates_user -> a new signup succeeds and returns
#    correct data (no password in the response)


def test_signup_creates_user():
    unique_email = f"pytest_{uuid.uuid4().hex[:8]}@example.com"

    response = client.post(
        "/users/signup",
        json={
            "username": "pytest_user1",
            "email": unique_email,
            "password": "testpassword123",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["email"] == unique_email
    assert "password" not in data
    assert "hashed_password" not in data
# 2. test_signup_rejects_duplicate_email -> signing up twice with
#    the same email fails with a 400 error
def test_signup_rejects_duplicate_email():
    client.post(
        "/users/signup",
        json={
            "username": "pytest_user2",
            "email": "pytest_duplicate@example.com",
            "password": "testpassword123",
        },
    )

    response = client.post(
        "/users/signup",
        json={
            "username": "pytest_user2b",
            "email": "pytest_duplicate@example.com",
            "password": "differentpassword456",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"
# 3. test_login_with_correct_credentials -> returns a valid token
def test_login_with_correct_credentials():
    unique_email = f"pytest_{uuid.uuid4().hex[:8]}@example.com"

    client.post(
        "/users/signup",
        json={
            "username": "pytest_login_user",
            "email": unique_email,
            "password": "correctpassword123",
        },
    )

    response = client.post(
        "/users/login",
        json={"email": unique_email, "password": "correctpassword123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
# 4. test_login_with_wrong_password -> fails with a 401 error
def test_login_with_wrong_password():
    unique_email = f"pytest_{uuid.uuid4().hex[:8]}@example.com"

    client.post(
        "/users/signup",
        json={
            "username": "pytest_wrongpass_user",
            "email": unique_email,
            "password": "correctpassword123",
        },
    )

    response = client.post(
        "/users/login",
        json={"email": unique_email, "password": "wrongpassword456"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

# 5. test_login_with_nonexistent_email -> fails with a 401 error
#    (same error as wrong password, so attackers can't tell which)
def test_login_with_nonexistent_email():
    response = client.post(
        "/users/login",
        json={"email": "definitely_not_a_real_user@example.com", "password": "anything123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
    """
tests/test_auth.py's role in the project:
Automated tests confirming the signup and login endpoints work
correctly, including proper rejection of bad attempts.

Core idea:
Uses FastAPI's TestClient to run the app in-memory without needing
a live server. Each test that requires a user generates a unique
email via uuid, so tests remain repeatable across runs rather than
depending on leftover data from previous test runs — a common
testing pitfall this suite deliberately avoids.
"""