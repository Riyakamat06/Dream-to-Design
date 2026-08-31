# This file defines endpoints for working with milestones and
# journal entries — the day-to-day tracking features once a
# dream's roadmap already exists.

# Endpoints needed:
# - PATCH /milestones/{id}/complete -> mark a milestone as done
# - POST /milestones/{id}/journal -> add a journal entry to a milestone
# - GET /milestones/{id}/journal -> fetch all journal entries for a milestone

# All of these require a logged-in user (get_current_user) —
# though note: right now we don't yet check that the milestone
# actually belongs to that user's own dream. That's a real gap
# worth flagging to Riya, since milestone ownership traces through
# Dream.user_id, which her routers/dreams.py will also need.