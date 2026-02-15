"""Web API routes (read-only)."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.services.task_service import TaskService
from app.domain.enums import TaskStatus
from app.web.schemas import TaskResponse, TaskDetailResponse, StatsResponse

router = APIRouter()


@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    status: Optional[TaskStatus] = None,
    assignee_telegram_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all tasks with optional filters."""
    service = TaskService(db)
    tasks = await service.get_all_tasks(status, assignee_telegram_id)
    return tasks


@router.get("/tasks/{task_id}", response_model=TaskDetailResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get task by ID with full details."""
    service = TaskService(db)
    task = await service.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.get("/tasks/week/current", response_model=List[TaskResponse])
async def get_week_tasks(db: AsyncSession = Depends(get_db)):
    """Get tasks for current week."""
    service = TaskService(db)
    tasks = await service.get_week_tasks()
    return tasks


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get task statistics."""
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
