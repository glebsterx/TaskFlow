"""Web API routes (with Telegram auth)."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.auth import verify_telegram_auth, create_access_token, get_current_user
from app.services.task_service import TaskService
from app.domain.enums import TaskStatus
from app.web.schemas import TaskResponse, TaskDetailResponse, StatsResponse, TelegramAuthRequest, TokenResponse

router = APIRouter()


@router.post("/auth/telegram", response_model=TokenResponse)
async def telegram_auth(auth_data: TelegramAuthRequest):
    """Authenticate with Telegram."""
    auth_dict = auth_data.model_dump()
    
    if not verify_telegram_auth(auth_dict):
        raise HTTPException(status_code=401, detail="Invalid Telegram authentication")
    
    access_token = create_access_token(auth_dict)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=auth_dict
    )


@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    status: Optional[TaskStatus] = None,
    assignee_telegram_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Protected route
):
    """Get all tasks with optional filters. Requires authentication."""
    service = TaskService(db)
    tasks = await service.get_all_tasks(status, assignee_telegram_id)
    return tasks


@router.get("/tasks/{task_id}", response_model=TaskDetailResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Protected route
):
    """Get task by ID with full details. Requires authentication."""
    service = TaskService(db)
    task = await service.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.get("/tasks/week/current", response_model=List[TaskResponse])
async def get_week_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Protected route
):
    """Get tasks for current week. Requires authentication."""
    service = TaskService(db)
    tasks = await service.get_week_tasks()
    return tasks


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Protected route
):
    """Get task statistics. Requires authentication."""
    service = TaskService(db)
    tasks = await service.get_all_tasks()
    
    stats = {
        "total": len(tasks),
        "todo": len([t for t in tasks if t.status == TaskStatus.TODO.value]),
        "doing": len([t for t in tasks if t.status == TaskStatus.DOING.value]),
        "done": len([t for t in tasks if t.status == TaskStatus.DONE.value]),
        "blocked": len([t for t in tasks if t.status == TaskStatus.BLOCKED.value]),
    }
    
    return stats


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info."""
    return current_user
