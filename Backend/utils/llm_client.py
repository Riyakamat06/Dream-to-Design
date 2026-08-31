"""
utils/llm_client.py

Wraps all interaction with the Gemini API in one place. No other file
in this project should import google.genai directly — every call to
the LLM goes through this module, so the rest of the app never needs
to know which provider we're using or how its API works.
"""

import json
import logging

from google import genai
from google.genai import types

from config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()
_client = genai.Client(api_key=settings.llm_api_key)

_MODEL_NAME = "gemini-3.6-flash"


class LLMGenerationError(Exception):
    """Raised when the LLM call fails or returns an unusable response."""
    pass


def generate_roadmap(dream_title: str, dream_description: str) -> list[dict]:
    """
    Given a dream's title and description, asks the LLM to generate a
    sequential list of milestones toward achieving it.

    Returns a list of dicts, each shaped like:
        {"title": str, "description": str, "order": int, "estimated_effort": str}

    Raises LLMGenerationError if the call fails or the response can't
    be parsed into that shape.
    """
    prompt = _build_prompt(dream_title, dream_description)

    try:
        response = _client.models.generate_content(
            model=_MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
    except Exception as exc:
        logger.error("Gemini API call failed: %s", exc)
        raise LLMGenerationError("Failed to reach the LLM service.") from exc

    return _parse_response(response.text)


def _build_prompt(title: str, description: str) -> str:
    return f"""You are helping a student break down a personal goal into a clear, achievable roadmap.

Goal title: {title}
Goal description: {description}

Generate 4 to 8 sequential milestones that lead to achieving this goal.
Respond ONLY with a JSON array, no other text, in this exact shape:

[
  {{
    "title": "short milestone title",
    "description": "1-2 sentence explanation of what to do",
    "order": 1,
    "estimated_effort": "e.g. '1 week', '3-4 days'"
  }}
]
"""


def _parse_response(raw_text: str) -> list[dict]:
    try:
        data = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.error("Could not parse LLM response as JSON: %s", raw_text)
        raise LLMGenerationError("The LLM returned an unreadable response.") from exc

    if not isinstance(data, list) or not data:
        raise LLMGenerationError("The LLM response was not a valid milestone list.")

    for milestone in data:
        if not all(k in milestone for k in ("title", "description", "order")):
            raise LLMGenerationError("A milestone in the LLM response was missing required fields.")

    return data
"""
- google.genai (new SDK) —  This file uses the new Client-based SDK instead.

- genai.Client(api_key=...) — One client object handles all requests; the model name is passed per-call instead of
  being baked into a separate model object, which makes it easy to swap models later
  without restructuring the file.

- "gemini-3.6-flash" — the current stable, generally-available Gemini Flash model as of
  now. gemini-1.5-flash is fully shut down; gemini-2.5-flash is already scheduled for
  shutdown in October. This model has no shutdown date yet, and Flash-tier models stay
  fast and free-tier-friendly, which is what this task needs.

- response_mime_type: "application/json" — tells Gemini to return valid JSON directly,
  rather than JSON wrapped in explanation text or markdown code fences. This is the
  "JSON mode" reliability the roadmap parsing depends on.

- LLMGenerationError — a custom exception, not a generic one. This matters because
  routers/dreams.py (built later) can specifically catch LLMGenerationError and turn it
  into a clean, user-facing error message — directly solving the "LLM call failure
  handling" requirement from the SRS (FR-LLM-03).

- _parse_response validates structure, not just JSON-ness — even if Gemini returns valid
  JSON, it checks each milestone actually has title, description, and order before
  trusting it. This protects routers/dreams.py from crashing later on missing fields.
"""