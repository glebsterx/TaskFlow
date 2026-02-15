"""Telegram command handlers."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.core.db import AsyncSessionLocal
from app.services.task_service import TaskService
from app.domain.enums import TaskStatus, TaskSource
from app.telegram.keyboards.task_keyboards import get_task_action_keyboard
from app.core.logging import get_logger

logger = get_logger(__name__)

router = Router()


class TaskCreationStates(StatesGroup):
    """States for task creation dialog."""
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_assignee = State()


@router.message(Command("task"))
async def cmd_task(message: Message, state: FSMContext):
    """Handle /task command - start task creation dialog."""
    await message.answer(
        "📝 Создание новой задачи\n\n"
        "Введите название задачи:"
    )
    await state.set_state(TaskCreationStates.waiting_for_title)


@router.message(TaskCreationStates.waiting_for_title)
async def process_task_title(message: Message, state: FSMContext):
    """Process task title input."""
    await state.update_data(title=message.text)
    await message.answer(
        "Отлично! Теперь введите описание задачи\n"
        "(или отправьте /skip чтобы пропустить):"
    )
    await state.set_state(TaskCreationStates.waiting_for_description)


@router.message(TaskCreationStates.waiting_for_description)
async def process_task_description(message: Message, state: FSMContext):
    """Process task description input."""
    
    data = await state.get_data()
    title = data.get("title")
    description = message.text if message.text != "/skip" else None
    
    # Create task
    async with AsyncSessionLocal() as session:
        service = TaskService(session)
        task = await service.create_task(
            title=title,
            description=description,
            source=TaskSource.MANUAL_COMMAND
        )
        await session.commit()
    
    await message.answer(
        f"✅ Задача создана!\n\n"
        f"#{task.id} {task.title}\n"
        f"Статус: {task.status}",
        reply_markup=get_task_action_keyboard(task.id)
    )
    
    await state.clear()
    logger.info("task_created_via_command", task_id=task.id)


@router.callback_query(F.data.startswith("task:"))
async def handle_task_action(callback: CallbackQuery):
    """Handle task action callbacks."""
    
    # Parse callback data: task:123:action
    parts = callback.data.split(":")
    if len(parts) != 3:
        return
    
    task_id = int(parts[1])
    action = parts[2]
    
    async with AsyncSessionLocal() as session:
        service = TaskService(session)
        
        try:
            if action == "start":
                task = await service.change_status(task_id, TaskStatus.DOING)
                await callback.answer("✅ Задача взята в работу")
                
            elif action == "done":
                task = await service.change_status(task_id, TaskStatus.DONE)
                await callback.answer("✅ Задача выполнена!")
                
            elif action == "block":
                # TODO: Implement blocker input dialog
                await callback.answer("🚫 Функция блокировки в разработке")
                return
            
            await session.commit()
            
            # Update message
            await callback.message.edit_text(
                f"#{task.id} {task.title}\n"
                f"Статус: {task.status}",
                reply_markup=get_task_action_keyboard(task.id)
            )
            
        except ValueError as e:
            await callback.answer(f"❌ Ошибка: {e}")
