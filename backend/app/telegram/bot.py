"""Telegram bot setup and runner."""
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import settings
from app.core.logging import get_logger
from app.telegram.handlers import task_handlers, week_handlers

logger = get_logger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


def setup_handlers():
    """Register all handlers."""
    dp.include_router(task_handlers.router)
    dp.include_router(week_handlers.router)
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
