"""Week board handler."""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.core.db import AsyncSessionLocal
from app.services.board_service import BoardService
from app.telegram.keyboards.task_keyboards import get_task_action_keyboard

router = Router()


@router.message(Command("week"))
async def cmd_week(message: Message):
    """Handle /week command - show weekly board."""
    
    async with AsyncSessionLocal() as session:
        board_service = BoardService(session)
        board = await board_service.get_week_board()
        board_message = board_service.format_board_message(board)
    
    await message.answer(board_message, parse_mode="Markdown")
    
    # Send tasks with action buttons (only non-done tasks)
    from app.domain.enums import TaskStatus
    for status in [TaskStatus.TODO.value, TaskStatus.DOING.value, TaskStatus.BLOCKED.value]:
        for task in board[status]:
            await message.answer(
                f"#{task.id} {task.title}\n"
                f"Статус: {task.status}",
                reply_markup=get_task_action_keyboard(task.id)
            )
