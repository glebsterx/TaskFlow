"""Help and menu handlers."""
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get main menu keyboard with all commands."""
    builder = InlineKeyboardBuilder()
    
    # First row - task management
    builder.row(
        InlineKeyboardButton(text="📝 Создать задачу", callback_data="cmd:task"),
        InlineKeyboardButton(text="📅 Недельная доска", callback_data="cmd:week")
    )
    
    # Second row - meetings and digest
    builder.row(
        InlineKeyboardButton(text="🤝 Фиксация встречи", callback_data="cmd:meeting"),
        InlineKeyboardButton(text="📊 Дайджест", callback_data="cmd:digest")
    )
    
    # Third row - lists
    builder.row(
        InlineKeyboardButton(text="📋 История встреч", callback_data="cmd:meetings"),
        InlineKeyboardButton(text="⏰ Просроченные", callback_data="cmd:overdue")
    )
    
    # Fourth row - help
    builder.row(
        InlineKeyboardButton(text="❓ Помощь", callback_data="cmd:help")
    )
    
    return builder.as_markup()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command."""
    await message.answer(
        f"👋 Привет! Я **TeamFlow** - бот для управления задачами команды.\n\n"
        f"Выберите действие:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Show main menu."""
    await message.answer(
        "📱 **Главное меню TeamFlow**\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Show help message."""
    help_text = """
🤖 **TeamFlow Bot - Справка**

**📝 Управление задачами:**
• `/task` или кнопка - создать новую задачу
• `/week` - показать недельную доску
• Напишите задачу в чат - бот предложит создать её автоматически

**🤝 Встречи:**
• `/meeting` - зафиксировать результаты встречи
• `/meetings` - показать историю встреч за месяц

**📊 Аналитика:**
• `/digest` - еженедельный дайджест
• `/overdue` - список просроченных задач

**💡 Советы:**
• Упоминайте @username для автоназначения исполнителя
• Указывайте даты: "завтра", "в пятницу", "через 3 дня"
• Используйте inline кнопки для быстрой работы

**🔧 Другое:**
• `/menu` - главное меню
• `/help` - эта справка

**📱 Web интерфейс:**
Откройте http://your-server:3333 для просмотра задач
"""
    
    await message.answer(
        help_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )


# Callback handlers for menu buttons
from aiogram import F
from aiogram.types import CallbackQuery


@router.callback_query(F.data.startswith("cmd:"))
async def handle_menu_callback(callback: CallbackQuery):
    """Handle menu button callbacks."""
    action = callback.data.split(":")[1]
    
    if action == "help":
        await cmd_help(callback.message)
        await callback.answer()
        return
    
    # For other commands, send the command as message
    command_map = {
        "task": "/task",
        "week": "/week",
        "meeting": "/meeting",
        "meetings": "/meetings",
        "digest": "/digest",
        "overdue": "/overdue",
    }
    
    if action in command_map:
        # Create a fake message to trigger command handler
        await callback.answer(f"Выполняю команду {command_map[action]}...")
        
        # Send command hint
        await callback.message.answer(
            f"Выполняю команду `{command_map[action]}`",
            parse_mode="Markdown"
        )
    else:
        await callback.answer("Команда не найдена")
