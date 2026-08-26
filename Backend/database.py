from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# This is the connection string — where our database file lives.
# For now we're using SQLite, which is just a single file, easy for a student project.
SQLALCHEMY_DATABASE_URL = "sqlite:///./dream_to_design.db"

# The "engine" is what actually talks to the database.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# A session is a temporary conversation with the database —
# used to read/write data, then closed.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the shared parent class every model (User, Dream, Milestone...)
# inherits from. It's what lets SQLAlchemy know these Python classes
# are meant to become real database tables.
Base = declarative_base()