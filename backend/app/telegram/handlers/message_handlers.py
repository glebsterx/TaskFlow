"""Message handler for automatic task detection."""
from aiogram import Router, F
from aiogram.types import Message
from app.core.db import AsyncSessionLocal
from app.services.task_service import TaskService
from app.services.message_parsing_service import MessageParsingService
from app.domain.enums import TaskSource
from app.telegram.keyboards.task_keyboards import get_confirmation_keyboard
from app.core.logging import get_logger
from app.config import settings

logger = get_logger(__name__)

router = Router()


@router.message(F.chat.id == settings.TELEGRAM_CHAT_ID)
async def process_chat_message(message: Message):
    """Process regular chat messages for task detection."""
    
    # Skip messages from bot itself
    if message.from_user.is_bot:
        return
    
    # Skip commands
    if message.text and message.text.startswith('/'):
        return
    
    # Parse message
    parser = MessageParsingService()
    candidate = parser.parse_message(
        text=message.text,
        entities=message.entities
    )
    
    if not candidate:
        return
    
    # Build confirmation message
    confirmation_text = (
        f"📋 Обнаружена задача!\n\n"
        f"**Название:** {candidate.text}\n"
    )
    
    if candidate.detected_assignee:
        confirmation_text += f"👤 **Исполнитель:** @{candidate.detected_assignee}\n"
    
    if candidate.detected_due_date:
        date_str = candidate.detected_due_date.strftime("%d.%m.%Y")
        confirmation_text += f"📅 **Срок:** {date_str}\n"
    
    confirmation_text += f"\n🎯 **Уверенность:** {int(candidate.confidence * 100)}%\n\n"
    confirmation_text += "Создать задачу?"
    
    # Store candidate data in callback
    callback_data = f"create_task:{message.message_id}"
    
    await message.reply(
        confirmation_text,
        reply_markup=get_confirmation_keyboard(message.message_id),
        parse_mode="Markdown"
    )
    
    logger.info(
        "task_candidate_proposed",
        message_id=message.message_id,
        confidence=candidate.confidence
    )
