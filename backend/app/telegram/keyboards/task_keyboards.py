"""Inline keyboards for tasks."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_task_action_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """Get inline keyboard with task actions."""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="▶️ Start", callback_data=f"task:{task_id}:start"),
            InlineKeyboardButton(text="✅ Done", callback_data=f"task:{task_id}:done"),
        ],
        [
            InlineKeyboardButton(text="🚫 Block", callback_data=f"task:{task_id}:block"),
        ]
    ])
    
    return keyboard


def get_confirmation_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """Get confirmation keyboard."""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data=f"confirm:{task_id}:yes"),
            InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"confirm:{task_id}:edit"),
            InlineKeyboardButton(text="❌ Нет", callback_data=f"confirm:{task_id}:no"),
        ]
    ])
    
    return keyboard
