# This script builds all database tables based on the models
# we've defined (User, Dream, Milestone, Reminder, Attachment).
# Run this once whenever a new model is added or changed.

from database import Base, engine
from models.user import User
from models.dream import Dream, Milestone, Reminder, Attachment

Base.metadata.create_all(bind=engine)

print("All tables created successfully.")
"""
create_tables.py's role in the project:
A one-time (or run-when-changed) script that builds the actual database
tables from our model definitions.

Core idea:
Turns Python class definitions (User, Dream, Milestone, etc.) into a
real, physical database file by calling Base.metadata.create_all().
This will likely be replaced by Alembic migrations once we set those up,
since this script can't safely update tables that already exist —
it can only create new ones.
"""