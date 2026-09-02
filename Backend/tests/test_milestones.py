import uuid
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models.dream import Dream, Milestone

client = TestClient(app)

# This file tests the milestone and journal entry endpoints,
# including the ownership check that ensures a user can only
# act on milestones belonging to their own dreams.

# Tests needed:
# 1. test_complete_own_milestone -> succeeds, persists is_completed=True
# 2. test_complete_nonexistent_milestone -> 404
# 3. test_complete_other_users_milestone -> 404 (ownership check)
# 4. test_add_journal_entry -> creates entry, returns correct shape
# 5. test_list_journal_entries -> returns all entries for a milestone
# 6. test_milestone_endpoints_require_auth -> no token -> 401/403


def _create_user_with_milestone():
    """
    Creates a fresh user via the real signup endpoint, then creates
    a dream and milestone directly in the database for that user
    (bypassing the LLM/dream-creation endpoints, which aren't what
    we're testing here). Returns (access_token, milestone_id).
    """
    unique_email = f"pytest_milestone_{uuid.uuid4().hex[:8]}@example.com"

    signup_response = client.post(
        "/users/signup",
        json={
            "username": "pytest_milestone_user",
            "email": unique_email,
            "password": "testpassword123",
        },
    )
    user_id = signup_response.json()["id"]

    login_response = client.post(
        "/users/login",
        json={"email": unique_email, "password": "testpassword123"},
    )
    access_token = login_response.json()["access_token"]

    db = SessionLocal()
    dream = Dream(user_id=user_id, title="Test Dream")
    db.add(dream)
    db.commit()
    db.refresh(dream)

    milestone = Milestone(dream_id=dream.id, title="Test Milestone", order=1)
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    milestone_id = milestone.id
    db.close()

    return access_token, milestone_id


# Test 1: completing your own milestone should succeed and persist
def test_complete_own_milestone():
    access_token, milestone_id = _create_user_with_milestone()

    response = client.patch(
        f"/milestones/{milestone_id}/complete",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == milestone_id
    assert data["is_completed"] is True


# Test 2: completing a milestone ID that doesn't exist should 404
def test_complete_nonexistent_milestone():
    access_token, _ = _create_user_with_milestone()

    response = client.patch(
        "/milestones/999999/complete",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404


# Test 3: the ownership check — User B must not be able to complete
# a milestone that belongs to User A's dream
def test_complete_other_users_milestone():
    _, milestone_id_a = _create_user_with_milestone()
    access_token_b, _ = _create_user_with_milestone()

    response = client.patch(
        f"/milestones/{milestone_id_a}/complete",
        headers={"Authorization": f"Bearer {access_token_b}"},
    )

    assert response.status_code == 404


# Test 4: adding a journal entry should succeed and return the
# correct shape, linked to the right milestone
def test_add_journal_entry():
    access_token, milestone_id = _create_user_with_milestone()

    response = client.post(
        f"/milestones/{milestone_id}/journal",
        json={"content": "Made great progress today!"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Made great progress today!"
    assert data["milestone_id"] == milestone_id


# Test 5: fetching journal entries should return every entry
# created for that milestone
def test_list_journal_entries():
    access_token, milestone_id = _create_user_with_milestone()

    client.post(
        f"/milestones/{milestone_id}/journal",
        json={"content": "First entry"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    client.post(
        f"/milestones/{milestone_id}/journal",
        json={"content": "Second entry"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    response = client.get(
        f"/milestones/{milestone_id}/journal",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


# Test 6: hitting a milestone endpoint with no auth token at all
# should be rejected, not silently allowed
def test_milestone_endpoints_require_auth():
    _, milestone_id = _create_user_with_milestone()

    response = client.patch(f"/milestones/{milestone_id}/complete")

    assert response.status_code == 401


"""
tests/test_milestones.py's role in the project:
Automated tests confirming milestone and journal entry endpoints
work correctly, including the ownership check that prevents one
user from acting on another user's milestones.

Core idea:
Uses a shared _create_user_with_milestone() helper to avoid
repeating the same setup (signup, login, create dream, create
milestone) in every test. Each test signs up a genuinely fresh
user via uuid, keeping tests repeatable across runs, the same
principle established in tests/test_auth.py.
"""