from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

from config import get_settings

settings = get_settings()



connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,  
)




SessionLocal = sessionmaker(
    autocommit=False,   
    autoflush=False,    
    bind=engine,
)



Base = declarative_base()



def get_db():
    """
    FastAPI dependency that provides a database session for the lifetime
    of a single request, and guarantees it is closed afterward — even if
    the request raises an exception.

    Usage in a router:
        @router.get("/dreams")
        def list_dreams(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError:
        db.rollback()
        raise
    finally:
        db.close()



def init_db():
    """Creates all tables directly from model metadata. Dev/testing use only."""
    Base.metadata.create_all(bind=engine)



""" Here's the full breakdown of what database.py does, section by section.

Overall purpose

This file is the connection layer between your Python code and the actual database file sitting on disk. It doesn't define 
what your data looks like (that's models/dream.py) and it doesn't contain any business logic (that's routers/dreams.py). 
Its entire job is: set up a working, safe connection to the database once, and hand it out cleanly to whoever needs it.

Section by section

The module docstring (top of file)
Explains the file's three responsibilities up front, and explicitly states what does not belong here (table definitions, 
business logic). This is a professional habit — anyone opening the file for the first time knows its scope before reading 
a line of code.

Section 1 — Engine
python
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

Checks whether you're using SQLite. SQLite normally only allows the thread that opened a connection to use it — but 
FastAPI can handle requests on different threads, so without this line, you'd hit random, confusing errors. This check means 
the fix only applies when needed; if you switch to PostgreSQL later, this line quietly does nothing.

python
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)

This is the actual live connection to your database. Three things worth noting:

It pulls the URL from config.py — never hardcoded here.
pool_pre_ping=True means before SQLAlchemy reuses a saved connection, it quickly checks the connection is still alive. 
Without this, a dropped connection (common in real deployments) could cause a confusing failure deep in your app instead of 
being caught and retried cleanly.
Only one engine is created for your whole app, ever. It's expensive to create and completely safe to share.

Section 2 — Session factory
python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

A session is one "conversation" with the database — you open it, read/write some data, then close it. SessionLocal isn't 
a session itself; it's a factory that creates fresh sessions on demand. autocommit=False and autoflush=False mean 
SQLAlchemy won't silently save changes to the database on its own — your code has to explicitly decide when to commit, 
which avoids accidental partial writes.

Section 3 — Declarative base
python
Base = declarative_base()

This is the shared foundation every table class in the whole project inherits from — your Dream, Milestone, Reminder, 
Attachment, and Sonali's User, JournalEntry. Because they all inherit from the same Base object, SQLAlchemy can resolve 
relationships and foreign keys between files written by different people (e.g. your Dream.user_id pointing at her User table), 
even though neither file imports the other directly.

Section 4 — get_db() dependency
python
def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError:
        db.rollback()
        raise
    finally:
        db.close()

This is the function your routers/dreams.py will use on every single endpoint. Walking through what it guarantees:

Opens a fresh session for this one request only (SessionLocal()).
- yield db hands that session to whatever endpoint is running — this is what makes it usable as a FastAPI dependency 
  (Depends(get_db)).
- If something goes wrong (except SQLAlchemyError), it rolls back any half-finished changes so your database never ends up 
  in a broken, partially-saved state.
- finally: db.close() — no matter what happens (success, failure, or an unrelated crash), the session is always closed. 
  This prevents a real, common bug in poorly-written backends: leaked, never-closed database connections that eventually exhaust the connection pool and crash the app under load.

Section 5 — init_db()
python
def init_db():
    Base.metadata.create_all(bind=engine)

A quick way to create all tables directly from your model definitions — useful for a fast local sanity check before Alembic 
migrations are set up. The docstring deliberately warns that real schema changes should go through Alembic, not this function, 
matching the database discipline practice from your project guide — this prevents you or Sonali from accidentally using this 
as a shortcut later and bypassing migration tracking.

The one core idea to remember

Every other backend file that needs the database goes through this file, never around it: models/dream.py imports Base 
from here, and routers/dreams.py will import get_db from here. One connection, one session pattern, used everywhere 
consistently.
"""
