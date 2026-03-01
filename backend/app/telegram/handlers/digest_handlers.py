"""Digest command handler."""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.core.db import AsyncSessionLocal
from app.services.digest_service import DigestService
from app.core.logging import get_logger

logger = get_logger(__name__)

router = Router()


@router.message(Command("digest"))
async def cmd_digest(message: Message):
    """Generate and send weekly digest."""
    from aiogram.enums import ChatAction
    from app.telegram.handlers.help_handlers import get_main_menu_keyboard
    
    try:
        # Показываем typing indicator
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        
        async with AsyncSessionLocal() as session:
            digest_service = DigestService(session)
            digest = await digest_service.generate_weekly_digest()
        
        await message.answer(digest, parse_mode="Markdown")
        await message.answer("📱 Главное меню:", reply_markup=get_main_menu_keyboard())
        logger.info("digest_sent")
        
    except Exception as e:
        logger.error("digest_generation_failed", error=str(e))
        await message.answer(
            f"❌ Ошибка при генерации дайджеста: {str(e)}\n\n"
            "Попробуйте позже или обратитесь к администратору."
        )


@router.message(Command("overdue"))
async def cmd_overdue(message: Message):
    """Show overdue tasks."""
    from app.telegram.handlers.help_handlers import get_main_menu_keyboard
    
    async with AsyncSessionLocal() as session:
        digest_service = DigestService(session)
        reminder = await digest_service.get_overdue_reminder()
    
    if reminder:
        await message.answer(reminder, parse_mode="Markdown")
    else:
        await message.answer("✅ Нет просроченных задач!")
    
    await message.answer("📱 Главное меню:", reply_markup=get_main_menu_keyboard())
    logger.info("overdue_check_sent")
