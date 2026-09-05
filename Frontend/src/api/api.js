// This file is the ONE place that talks to our backend.
// Every component that needs data calls a function from here,
// instead of writing fetch() calls scattered across components.

// Why centralize this?
// - If the backend URL changes, we only update it in one place
// - If we need to attach the auth token to every request, we
//   only write that logic once, here
// - Keeps components focused on UI, not networking details

// Functions needed:
// - signup(username, email, password)
// - login(email, password)
// - getCurrentUser(token)
// - completeMilestone(milestoneId, token)
// - addJournalEntry(milestoneId, content, token)
// - getJournalEntries(milestoneId, token)

const BASE_URL = "http://localhost:8000";

// Shared request helper — every function below calls this instead
// of writing its own fetch() logic. Handles the base URL, default
// headers, and turning a failed response into a real JS error.
async function request(endpoint, options = {}) {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Something went wrong");
  }

  return response.json();
}

// Auth functions — signup/login don't need a token (the user
// doesn't have one yet); everything after login does.

export async function signup(username, email, password) {
  return request("/users/signup", {
    method: "POST",
    body: JSON.stringify({ username, email, password }),
  });
}

export async function login(email, password) {
  return request("/users/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function getCurrentUser(token) {
  return request("/users/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

// Milestone and journal functions — all require a valid token,
// since these endpoints are protected by get_current_user on
// the backend.

export async function completeMilestone(milestoneId, token) {
  return request(`/milestones/${milestoneId}/complete`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export async function addJournalEntry(milestoneId, content, token) {
  return request(`/milestones/${milestoneId}/journal`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ content }),
  });
}

export async function getJournalEntries(milestoneId, token) {
  return request(`/milestones/${milestoneId}/journal`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

// api/api.js's role in the project:
// The single, centralized place every component uses to talk to
// the backend — no component writes its own fetch() calls directly.
//
// Core idea:
// A shared request() helper handles the base URL, default headers,
// and error handling once, so every exported function here stays
// short and focused only on which endpoint it calls and what data
// it sends. Functions needing authentication accept a token
// parameter and attach it as a Bearer header, mirroring exactly how
// get_current_user expects to receive it on the backend.