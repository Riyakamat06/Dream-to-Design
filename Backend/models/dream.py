# backend/models/dream.py

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Dream(Base):
    __tablename__ = "dreams"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    status = Column(String, default="not_started")
    target_date = Column(Date, nullable=True)
    progress_percentage = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user = relationship("User", back_populates="dreams")  

    milestones = relationship("Milestone", back_populates="dream", cascade="all, delete-orphan")


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    dream_id = Column(Integer, ForeignKey("dreams.id"), nullable=False)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, nullable=False)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(Date, nullable=True)
    estimated_effort = Column(String, nullable=True)

    dream = relationship("Dream", back_populates="milestones")
    reminders = relationship("Reminder", back_populates="milestone", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="milestone", cascade="all, delete-orphan")
    journal_entries = relationship("JournalEntry", back_populates="milestone", cascade="all, delete-orphan")


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=False)

    remind_at = Column(DateTime(timezone=True), nullable=False)
    is_dismissed = Column(Boolean, default=False)

    milestone = relationship("Milestone", back_populates="reminders")


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=False)

    file_url = Column(String, nullable=False)
    file_type = Column(String, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    milestone = relationship("Milestone", back_populates="attachments")



    """Here's the plain-language summary of what models/dream.py does, plus a walkthrough of the 
    important lines.

What the file does, overall

It defines the database table structure for everything related to a user's dream: the dream itself, 
its milestones, reminders tied to milestones, and file attachments tied to milestones. 
Each Python class in this file becomes an actual table in your database once you run a migration. 
This is your data layer — nothing in here handles requests or logic, it only describes what 
data looks like and how it's related.

There are four classes = four tables: Dream, Milestone, Reminder, Attachment.

Important lines and their role

from database import Base
Every model in your whole project (yours and Sonali's) needs to inherit from this same Base object.
It's what lets SQLAlchemy know "these Python classes are database tables" and lets it wire up 
relationships between tables defined in different files, like Dream (your file) and 
User (Sonali's file).

class Dream(Base):
This line is what actually turns a plain Python class into a real database table. Without 
inheriting Base, it's just a class — SQLAlchemy wouldn't know to create a table for it.

__tablename__ = "dreams"
The literal name of the table in the database. This is also what other files reference when creating
foreign keys — like ForeignKey("dreams.id") in your Milestone class.

id = Column(Integer, primary_key=True, index=True)
Every table needs a unique identifier. primary_key=True makes this the unique row identifier; 
index=True makes lookups by id fast.

user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
This is how Dream connects to User — even though User lives in Sonali's file, not yours. 
ForeignKey("users.id") references the table name as a string, so it works even before her file exists.

status = Column(String, default="not_started")
default= means if nothing is provided when a Dream is created, this value is used automatically 
— you don't need to set it manually every time in your endpoint code.

created_at = Column(DateTime(timezone=True), server_default=func.now())
server_default=func.now() means the database itself stamps the time, not your Python code. 
This avoids bugs where your server's clock and the database's clock disagree.

milestones = relationship("Milestone", back_populates="dream", cascade="all, delete-orphan")
This is not a real database column — it's a SQLAlchemy convenience. It lets you write 
some_dream.milestones in Python and get a list of related Milestone objects automatically, 
without writing a manual SQL join. cascade="all, delete-orphan" is important: it means if you 
delete a Dream, all its Milestones are automatically deleted too — no orphaned rows left behind.

dream_id = Column(Integer, ForeignKey("dreams.id"), nullable=False) (in Milestone)
This is the reverse side of the relationship above — it's what actually links a milestone row back 
to its parent dream in the database.

dream = relationship("Dream", back_populates="milestones") (in Milestone)
The mirror image of the milestones relationship on Dream. This lets you write 
some_milestone.dream to get back the parent dream object. back_populates is what tells 
SQLAlchemy these two relationships are two sides of the same connection.

reminders = relationship(...) and attachments = relationship(...) (in Milestone)
Same pattern again — lets you access some_milestone.reminders and some_milestone.attachments 
directly, and cascades their deletion when a milestone is deleted.

The big picture pattern to notice

Every relationship in this file appears in pairs: a ForeignKey column (the real database link) 
plus a relationship() (the Python convenience layer), on both sides. That pairing is what makes 
SQLAlchemy able to navigate dream.milestones, milestone.dream, milestone.reminders, etc. — all 
without you writing manual SQL joins anywhere in your endpoint code later."""