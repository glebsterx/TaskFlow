"""Domain models."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.domain.enums import TaskStatus, TaskSource


class Task(Base):
    """Task entity."""
    
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Assignee info
    assignee_name = Column(String(100), nullable=True)
    assignee_telegram_id = Column(Integer, nullable=True)
    
    # Status and dates
    status = Column(String(20), nullable=False, default=TaskStatus.TODO.value)
    due_date = Column(DateTime, nullable=True)
    definition_of_done = Column(Text, nullable=True)
    
    # Source tracking
    source = Column(String(20), nullable=False)
    source_message_id = Column(Integer, nullable=True)
    source_chat_id = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    blockers = relationship("Blocker", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"


class Blocker(Base):
    """Blocker entity - describes task obstacles."""
    
    __tablename__ = "blockers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_by = Column(Integer, nullable=True)  # Telegram user ID
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="blockers")
    
    def __repr__(self) -> str:
        return f"<Blocker(id={self.id}, task_id={self.task_id})>"


class Meeting(Base):
    """Meeting entity - team meeting records."""
    
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_date = Column(DateTime, nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<Meeting(id={self.id}, date={self.meeting_date})>"
