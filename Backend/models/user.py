from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


# This file defines the User table — every student who signs up
# gets one row here. Other tables (like Dream) link back to this
# table using a user_id foreign key.

class User(Base):
    __tablename__ = "users"

    # a unique id
    id = Column(Integer, primary_key=True, index=True)

    # a username
    username = Column(String, nullable=False)

    # an email (must be unique — no two users share one)
    email = Column(String, unique=True, nullable=False)

    # a hashed password (never store the real password!)
    hashed_password = Column(String, nullable=False)

    # when they signed up
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # a user can have many dreams
    dreams = relationship("Dream", back_populates="user")