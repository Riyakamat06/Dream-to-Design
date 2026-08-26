# This script builds all database tables based on the models
# we've defined (User, Dream, Milestone, Reminder, Attachment).
# Run this once whenever a new model is added or changed.

from database import Base, engine
from models.user import User
from models.dream import Dream, Milestone, Reminder, Attachment

Base.metadata.create_all(bind=engine)

print("All tables created successfully.")