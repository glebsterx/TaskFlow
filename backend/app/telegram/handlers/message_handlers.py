"""Message handler — умная эвристика для автосоздания задач."""
import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.core.db import AsyncSessionLocal
from app.services.task_service import TaskService
from app.repositories.user_repository import UserRepository
from app.domain.enums import TaskSource
from app.telegram.keyboards.task_keyboards import get_confirmation_keyboard
from app.core.logging import get_logger

logger = get_logger(__name__)
router = Router()

# Расширенные ключевые слова для автосоздания задач
TASK_KEYWORDS = re.compile(
    r'\b('
    # Русские императивы
    r'нужно|надо|необходимо|требуется|'
    r'сделай|сделать|создай|создать|добавь|добавить|'
    r'исправь|исправить|почини|починить|'
    r'проверь|проверить|протестируй|протестировать|'
    r'реализуй|реализовать|внедри|внедрить|'
    r'разберись|разобраться|посмотри|посмотреть|'
    r'не забудь|не забыть|напомни|напомнить|'
    r'задача|задачу|поручение|запланируй|запланировать|'
    # Английские
    r'todo|task|need to|needs to|have to|must|should|'
    r'please do|please|fix|create|add|implement|'
    r'check|test|review|remind|remember|'
    r'make sure|don\'t forget'
    r')\b',
    re.IGNORECASE
)

# Паттерны поручений (более сложная эвристика)
ASSIGNMENT_PATTERNS = [
    re.compile(r'@\w+[,\s]+(нужно|надо|сделай|проверь|исправь)', re.IGNORECASE),
    re.compile(r'(нужно|надо)\s+@\w+', re.IGNORECASE),
    re.compile(r'(сделай|сделать|проверь|проверить|исправь|исправить)\s+\S+', re.IGNORECASE),
]

MIN_MESSAGE_LEN = 10  # Минимум символов


def count_words(text: str) -> int:
    """Считает слова в тексте."""
    return len(text.split())


def is_task_like_message(text: str) -> bool:
    """Проверяет похоже ли сообщение на задачу/поручение."""
    if len(text) < MIN_MESSAGE_LEN:
        return False
    
    # Минимум 5 слов включая ключевое слово
    if count_words(text) < 5:
        return False
    
    # Проверка ключевых слов
    if TASK_KEYWORDS.search(text):
        return True
    
    # Проверка паттернов поручений
    for pattern in ASSIGNMENT_PATTERNS:
        if pattern.search(text):
            return True
    
    # Вопросительные предложения обычно не задачи
    if text.strip().endswith('?') and not any(kw in text.lower() for kw in ['нужно', 'надо', 'сделать']):
        return False
    
    return False


def extract_task_title(text: str) -> str:
    """Вырезаем ключевое слово из начала и возвращаем суть."""
    cleaned = re.sub(
        r'^(нужно|надо|необходимо|требуется|сделай|сделать|создай|создать|'
        r'добавь|добавить|исправь|исправить|почини|починить|'
        r'проверь|проверить|протестируй|протестировать|'
        r'реализуй|реализовать|внедри|внедрить|'
        r'разберись|разобраться|посмотри|посмотреть|'
        r'не забудь|не забыть|напомни|напомнить|'
        r'задача|задачу|поручение|запланируй|запланировать|'
        r'todo|task|need to|needs to|have to|must|should|'
        r'please do|please|fix|create|add|implement|'
        r'check|test|review|remind|remember|'
        r'make sure|don\'t forget)[:\s]+',
        '', text.strip(), flags=re.IGNORECASE
    ).strip()
    return cleaned[:200] if cleaned else text[:200]


def make_assign_keyboard(task_id: int, users: list) -> InlineKeyboardMarkup:
    """Клавиатура назначения после создания задачи."""
    buttons = [[
        InlineKeyboardButton(text="👤 Взять себе", callback_data=f"self_assign:{task_id}")
    ]]
    
    for user in users[:5]:
        buttons.append([
            InlineKeyboardButton(
                text=f"👤 {user.display_name}",
                callback_data=f"assign_new:{task_id}:{user.telegram_id}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="📋 Без исполнителя", callback_data=f"skip_assign:{task_id}")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Хранилище ожидающих подтверждения
_pending = {}


@router.message(F.text)
async def handle_potential_task(message: Message):
    """Обработчик всех текстовых сообщений — детектирует задачи."""
    text = message.text
    
    if not is_task_like_message(text):
        return
    
    # Сохраняем в ожидании подтверждения
    msg_id = message.message_id
    _pending[msg_id] = {
        'text': text,
        'chat_id': message.chat.id,
        'from_user': message.from_user.id
    }
    
    await message.reply(
        f"💡 Обнаружена задача!\n\n*Создать задачу?*\n_{extract_task_title(text)}_",
        reply_markup=get_confirmation_keyboard(msg_id),
        parse_mode="Markdown"
    )
    logger.info("task_suggestion", message_id=msg_id)


@router.callback_query(F.data.startswith("confirm_task:"))
async def handle_confirm_task(callback: CallbackQuery, tg_user_id: int = 0):
    """Подтверждение создания задачи."""
    msg_id = int(callback.data.split(":")[1])
    
    if msg_id not in _pending:
        await callback.answer("⏱️ Время подтверждения истекло")
        return
    
    pending = _pending.pop(msg_id)
    title = extract_task_title(pending['text'])
    
    async with AsyncSessionLocal() as session:
        service = TaskService(session)
        task = await service.create_task(
            title=title,
            source=TaskSource.AUTO_KEYWORD,
            source_message_id=msg_id,
            source_chat_id=pending['chat_id']
        )
        
        # Получаем список пользователей для назначения
        user_repo = UserRepository(session)
        users = await user_repo.get_all()
        
        await session.commit()
    
    await callback.message.edit_text(
        f"✅ *Задача создана!*\n\n#{task.id} {task.title}\n\n👤 Назначить исполнителя:",
        reply_markup=make_assign_keyboard(task.id, users),
        parse_mode="Markdown"
    )
    await callback.answer()
    logger.info("task_created_from_keyword", task_id=task.id)


@router.callback_query(F.data.startswith("cancel_task:"))
async def handle_cancel_task(callback: CallbackQuery):
    """Отмена создания задачи."""
    msg_id = int(callback.data.split(":")[1])
    _pending.pop(msg_id, None)
    
    await callback.message.edit_text("❌ Отменено")
    await callback.answer()


@router.callback_query(F.data.startswith("self_assign:"))
async def handle_self_assign(callback: CallbackQuery, tg_user_id: int = 0):
    """Взять задачу себе."""
    task_id = int(callback.data.split(":")[1])
    
    async with AsyncSessionLocal() as session:
        service = TaskService(session)
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(tg_user_id)
        
        if user:
            await service.take_task(task_id, user)
            await session.commit()
    
    await callback.message.edit_text(
        f"✅ Задача #{task_id} взята в работу!\n👤 Исполнитель: {user.display_name}"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("assign_new:"))
async def handle_assign_new(callback: CallbackQuery):
    """Назначить задачу конкретному пользователю."""
    parts = callback.data.split(":")
    task_id = int(parts[1])
    user_telegram_id = int(parts[2])
    
    async with AsyncSessionLocal() as session:
        service = TaskService(session)
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(user_telegram_id)
        
        if user:
            await service.assign_task(task_id, user)
            await session.commit()
    
    await callback.message.edit_text(
        f"✅ Задача #{task_id} назначена!\n👤 Исполнитель: {user.display_name}"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("skip_assign:"))
async def handle_skip_assign(callback: CallbackQuery):
    """Пропустить назначение исполнителя."""
    task_id = int(callback.data.split(":")[1])
    
    await callback.message.edit_text(f"✅ Задача #{task_id} создана без исполнителя")
    await callback.answer()
