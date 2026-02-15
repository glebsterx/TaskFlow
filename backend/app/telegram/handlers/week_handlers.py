"""Week board handler."""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.core.db import AsyncSessionLocal
from app.services.task_service import TaskService
from app.domain.enums import TaskStatus
from app.telegram.keyboards.task_keyboards import get_task_action_keyboard

router = Router()


@router.message(Command("week"))
async def cmd_week(message: Message):
    """Handle /week command - show weekly board."""
    
    async with AsyncSessionLocal() as session:
        service = TaskService(session)
        tasks = await service.get_week_tasks()
    
    if not tasks:
        await message.answer("📋 На этой неделе пока нет задач")
        return
    
    # Group tasks by status
    grouped = {
        TaskStatus.TODO: [],
        TaskStatus.DOING: [],
        TaskStatus.DONE: [],
        TaskStatus.BLOCKED: []
    }
    
    for task in tasks:
        status = TaskStatus(task.status)
        grouped[status].append(task)
    
    # Build message
    text = "📅 Недельная доска задач\n\n"
    
    status_emoji = {
        TaskStatus.TODO: "📝",
        TaskStatus.DOING: "🔄",
        TaskStatus.DONE: "✅",
        TaskStatus.BLOCKED: "🚫"
    }
    
    status_names = {
        TaskStatus.TODO: "К выполнению",
        TaskStatus.DOING: "В работе",
        TaskStatus.DONE: "Выполнено",
        TaskStatus.BLOCKED: "Заблокировано"
    }
    
    for status in [TaskStatus.TODO, TaskStatus.DOING, TaskStatus.DONE, TaskStatus.BLOCKED]:
        if grouped[status]:
            text += f"\n{status_emoji[status]} {status_names[status]}:\n"
            for task in grouped[status]:
                assignee = f"👤 {task.assignee_name}" if task.assignee_name else ""
                text += f"  #{task.id} {task.title} {assignee}\n"
    
    await message.answer(text)
    
    # Send each task with action buttons
    for task in tasks:
        if task.status != TaskStatus.DONE.value:
            await message.answer(
                f"#{task.id} {task.title}\n"
                f"Статус: {task.status}",
                reply_markup=get_task_action_keyboard(task.id)
            )
