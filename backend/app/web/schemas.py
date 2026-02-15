"""Pydantic schemas for Web API."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class BlockerResponse(BaseModel):
    """Blocker response schema."""
    id: int
    task_id: int
    text: str
    created_by: Optional[int]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TaskResponse(BaseModel):
    """Task response schema."""
    id: int
    title: str
    description: Optional[str]
    assignee_name: Optional[str]
    assignee_telegram_id: Optional[int]
    status: str
    due_date: Optional[datetime]
    definition_of_done: Optional[str]
    source: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TaskDetailResponse(TaskResponse):
    """Task detail response with blockers."""
    blockers: List[BlockerResponse] = []
    source_message_id: Optional[int]
    source_chat_id: Optional[int]


class StatsResponse(BaseModel):
    """Statistics response."""
    total: int
    todo: int
    doing: int
    done: int
    blocked: int


class TelegramAuthRequest(BaseModel):
    """Telegram authentication request."""
    id: int
    first_name: str
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str


class TokenResponse(BaseModel):
    """Token response after authentication."""
    access_token: str
    token_type: str
    user: dict
