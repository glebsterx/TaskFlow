"""Telegram bot setup and runner."""
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.config import settings
from app.core.logging import get_logger
from app.telegram.handlers import (
    help_handlers,
    task_handlers,
    week_handlers,
    meeting_handlers,
    digest_handlers,
    message_handlers
)

logger = get_logger(__name__)

# Initialize bot with default parse mode
bot = Bot(
    token=settings.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


def setup_handlers():
    """Register all handlers in priority order."""
    # Help and menu (highest priority)
    dp.include_router(help_handlers.router)
    
    # Command handlers
    dp.include_router(task_handlers.router)
    dp.include_router(week_handlers.router)
    dp.include_router(meeting_handlers.router)
    dp.include_router(digest_handlers.router)
    
    # Message handler (lowest priority, catches all messages)
    dp.include_router(message_handlers.router)
    
    logger.info("handlers_registered")


async def start_bot():
    """Start the bot."""
    setup_handlers()
    logger.info("bot_starting")
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


def run_bot():
    """Run bot in event loop."""
    asyncio.run(start_bot())
