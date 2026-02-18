"""Команда /tasks — список задач кнопками с деталями."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.core.db import AsyncSessionLocal
from app.services.task_service import TaskService
from app.repositories.user_repository import UserRepository
from app.domain.enums import TaskStatus
from app.domain.models import TelegramUser
from app.core.logging import get_logger

logger = get_logger(__name__)
router = Router()

STATUS_EMOJI = {"TODO": "📝", "DOING": "🔄", "DONE": "✅", "BLOCKED": "🚫"}


def tasks_list_keyboard(filter_status: str = "all", show_mine: bool = False, show_projects: bool = False) -> InlineKeyboardMarkup:
    """Фильтры для списка."""
    def btn(text, data):
        return InlineKeyboardButton(text=text, callback_data=data)

    buttons = [
        [
            btn("📋 Все" if filter_status != "all" else "📋 ●Все", "tasks:all"),
            btn("📝 TODO" if filter_status != "TODO" else "📝 ●TODO", "tasks:TODO"),
        ],
        [
            btn("🔄 В работе" if filter_status != "DOING" else "🔄 ●В работе", "tasks:DOING"),
            btn("✅ Готово" if filter_status != "DONE" else "✅ ●Готово", "tasks:DONE"),
        ],
        [
            btn("🚫 Блок" if filter_status != "BLOCKED" else "🚫 ●Блок", "tasks:BLOCKED"),
            btn("👤 Мои" if not show_mine else "👤 ●Мои", "tasks:mine"),
        ],
        [
            btn("📁 По проектам" if not show_projects else "📁 ●По проектам", "tasks:projects"),
            btn("🔄 Обновить", "tasks:refresh"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def task_buttons_keyboard(tasks: list, page: int = 0, per_page: int = 8) -> InlineKeyboardMarkup:
    """Список задач кнопками (до 8 на странице)."""
    start = page * per_page
    end = start + per_page
    page_tasks = tasks[start:end]
    
    buttons = []
    for task in page_tasks:
        emoji = STATUS_EMOJI.get(task.status, "•")
        assignee = f" → {task.assignee.display_name}" if task.assignee else ""
        text = f"{emoji} #{task.id} {task.title[:30]}{assignee}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"task_detail:{task.id}")])
    
    # Пагинация если > per_page
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"tasks_page:{page-1}"))
    if end < len(tasks):
        nav.append(InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"tasks_page:{page+1}"))
    if nav:
        buttons.append(nav)
    
    buttons.append([InlineKeyboardButton(text="🔍 Фильтры", callback_data="show_filters")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def task_detail_keyboard(task_id: int, status: str, assignee_telegram_id: int = None, current_user_tg_id: int = None) -> InlineKeyboardMarkup:
    """Действия с задачей."""
    buttons = []

    # Взять / Назначить / Снять
    if not assignee_telegram_id:
        buttons.append([
            InlineKeyboardButton(text="👤 Взять себе", callback_data=f"take_task:{task_id}"),
            InlineKeyboardButton(text="👥 Назначить...", callback_data=f"assign_menu:{task_id}"),
        ])
    elif assignee_telegram_id == current_user_tg_id:
        buttons.append([
            InlineKeyboardButton(text="❌ Снять с себя", callback_data=f"unassign:{task_id}"),
            InlineKeyboardButton(text="👥 Переназначить", callback_data=f"assign_menu:{task_id}"),
        ])
    else:
        buttons.append([
            InlineKeyboardButton(text="❌ Снять исполнителя", callback_data=f"unassign:{task_id}"),
            InlineKeyboardButton(text="👥 Переназначить", callback_data=f"assign_menu:{task_id}"),
        ])

    # Смена статуса
    if status == "TODO":
        buttons.append([InlineKeyboardButton(text="▶️ В работу", callback_data=f"task_status:{task_id}:DOING")])
    elif status == "DOING":
        buttons.append([
            InlineKeyboardButton(text="✅ Выполнено", callback_data=f"task_status:{task_id}:DONE"),
            InlineKeyboardButton(text="🚫 Заблокировать", callback_data=f"task_status:{task_id}:BLOCKED"),
        ])
    elif status == "BLOCKED":
        buttons.append([InlineKeyboardButton(text="▶️ Возобновить", callback_data=f"task_status:{task_id}:DOING")])
    elif status == "DONE":
        buttons.append([InlineKeyboardButton(text="🔄 Переоткрыть", callback_data=f"task_status:{task_id}:TODO")])

    buttons.append([InlineKeyboardButton(text="↩️ К списку", callback_data="tasks:all")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def assign_keyboard(task_id: int, users: list[TelegramUser]) -> InlineKeyboardMarkup:
    """Выбор исполнителя."""
    buttons = []
    for user in users[:10]:
        buttons.append([InlineKeyboardButton(
            text=f"👤 {user.display_name}",
            callback_data=f"assign:{task_id}:{user.telegram_id}"
        )])
    buttons.append([InlineKeyboardButton(text="↩️ Назад к задаче", callback_data=f"task_detail:{task_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Кеш текущих задач в памяти (для пагинации)
_task_cache = {}


@router.message(Command("tasks"))
async def cmd_tasks(message: Message):
    """Показать фильтры задач."""
    await message.answer(
        "📋 *Список задач*\n\nВыберите фильтр:",
        reply_markup=tasks_list_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "show_filters")
async def show_filters(callback: CallbackQuery):
    """Вернуться к фильтрам."""
    await callback.message.edit_text(
        "📋 *Список задач*\n\nВыберите фильтр:",
        reply_markup=tasks_list_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("tasks:"))
async def handle_tasks_filter(callback: CallbackQuery, tg_user_id: int = 0):
    """Фильтрация → показ кнопок с задачами."""
    action = callback.data.split(":")[1]

    try:
        if action == "projects":
            # Показываем список проектов
            async with AsyncSessionLocal() as session:
                from app.repositories.project_repository import ProjectRepository
                repo = ProjectRepository(session)
                projects = await repo.get_all_active()

            if not projects:
                await callback.message.edit_text(
                    "📁 *Проекты*\n\nПроектов пока нет.\n"
                    "Создайте проект командой /project",
                    reply_markup=tasks_list_keyboard(),
                    parse_mode="Markdown"
                )
            else:
                buttons = []
                for proj in projects:
                    emoji = proj.emoji or "📁"
                    buttons.append([InlineKeyboardButton(
                        text=f"{emoji} {proj.name}",
                        callback_data=f"tasks_project:{proj.id}"
                    )])
                buttons.append([InlineKeyboardButton(text="📋 Без проекта", callback_data="tasks_project:0")])
                buttons.append([InlineKeyboardButton(text="↩️ Назад", callback_data="tasks:all")])

                await callback.message.edit_text(
                    "📁 *Выберите проект*",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
                    parse_mode="Markdown"
                )
            await callback.answer()
            return

        async with AsyncSessionLocal() as session:
            service = TaskService(session)

            if action == "mine":
                tasks = await service.get_all_tasks()
                tasks = [t for t in tasks if t.assignee_telegram_id == tg_user_id]
                header = "👤 Мои задачи"
            elif action in ("TODO", "DOING", "DONE", "BLOCKED"):
                status = TaskStatus(action)
                tasks = await service.get_all_tasks(status=status)
                header = f"{STATUS_EMOJI[action]} {action}"
            else:  # all / refresh
                tasks = await service.get_all_tasks()
                header = "📋 Все задачи"

        if not tasks:
            await callback.message.edit_text(
                f"{header}\n\n✨ Задач нет",
                reply_markup=tasks_list_keyboard(action, action == "mine", False)
            )
        else:
            _task_cache[callback.from_user.id] = tasks
            await callback.message.edit_text(
                f"{header} ({len(tasks)})\n\nВыберите задачу:",
                reply_markup=task_buttons_keyboard(tasks, page=0)
            )
        await callback.answer()

    except Exception as e:
        logger.error("tasks_filter_error", error=str(e))
        await callback.answer("❌ Ошибка")


@router.callback_query(F.data.startswith("tasks_page:"))
async def handle_tasks_page(callback: CallbackQuery):
    """Пагинация списка задач."""
    page = int(callback.data.split(":")[1])
    tasks = _task_cache.get(callback.from_user.id, [])
    
    await callback.message.edit_text(
        f"📋 Задачи (стр. {page+1})\n\nВыберите задачу:",
        reply_markup=task_buttons_keyboard(tasks, page=page)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("task_detail:"))
async def handle_task_detail(callback: CallbackQuery, tg_user_id: int = 0):
    """Показать детали задачи."""
    task_id = int(callback.data.split(":")[1])
    
    try:
        async with AsyncSessionLocal() as session:
            service = TaskService(session)
            task = await service.get_task(task_id)
            
            if not task:
                await callback.answer("❌ Задача не найдена")
                return
        
        assignee_str = f"\n👤 Исполнитель: {task.assignee.display_name}" if task.assignee else "\n👤 Не назначено"
        desc = f"\n\n{task.description}" if task.description else ""
        
        text = (
            f"{STATUS_EMOJI[task.status]} *Задача #{task.id}*\n"
            f"{task.title}{assignee_str}"
            f"{desc}\n\n"
            f"Статус: {task.status}"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=task_detail_keyboard(
                task.id, task.status,
                task.assignee_telegram_id,
                tg_user_id
            ),
            parse_mode="Markdown"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error("task_detail_error", error=str(e))
        await callback.answer("❌ Ошибка")


@router.callback_query(F.data.startswith("take_task:"))
async def handle_take_task(callback: CallbackQuery, tg_user_id: int = 0):
    """Взять задачу себе."""
    task_id = int(callback.data.split(":")[1])
    
    try:
        async with AsyncSessionLocal() as session:
            service = TaskService(session)
            user_repo = UserRepository(session)
            
            user = await user_repo.get_by_telegram_id(tg_user_id)
            if not user:
                await callback.answer("❌ Пользователь не найден")
                return
            
            task = await service.take_task(task_id, user)
            await session.commit()
        
        await callback.answer(f"✅ Задача взята в работу")
        # Показываем обновлённую задачу
        await handle_task_detail(callback, tg_user_id)
        
    except Exception as e:
        logger.error("take_task_error", error=str(e))
        await callback.answer("❌ Ошибка")


@router.callback_query(F.data.startswith("task_status:"))
async def handle_task_status_change(callback: CallbackQuery):
    """Смена статуса задачи."""
    parts = callback.data.split(":")
    task_id = int(parts[1])
    new_status = TaskStatus(parts[2])
    
    try:
        async with AsyncSessionLocal() as session:
            service = TaskService(session)
            await service.change_status(task_id, new_status)
            await session.commit()
        
        await callback.answer(f"✅ Статус изменён на {new_status.value}")
        # Показываем обновлённую задачу
        await handle_task_detail(callback)
        
    except Exception as e:
        logger.error("status_change_error", error=str(e))
        await callback.answer("❌ Ошибка")


@router.callback_query(F.data.startswith("assign_menu:"))
async def handle_assign_menu(callback: CallbackQuery):
    """Меню выбора исполнителя."""
    task_id = int(callback.data.split(":")[1])
    
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        users = await user_repo.get_all()
    
    if not users:
        await callback.answer("❌ Нет пользователей")
        return
    
    await callback.message.edit_text(
        f"👤 *Назначить задачу #{task_id}*\n\nВыберите исполнителя:",
        reply_markup=assign_keyboard(task_id, users),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("assign:"))
async def handle_assign(callback: CallbackQuery):
    """Назначить задачу."""
    parts = callback.data.split(":")
    task_id = int(parts[1])
    assignee_telegram_id = int(parts[2])
    
    try:
        async with AsyncSessionLocal() as session:
            service = TaskService(session)
            user_repo = UserRepository(session)
            
            user = await user_repo.get_by_telegram_id(assignee_telegram_id)
            if not user:
                await callback.answer("❌ Пользователь не найден")
                return
            
            task = await service.assign_task(task_id, user)
            await session.commit()
        
        await callback.answer(f"✅ Назначено на {user.display_name}")
        # Возвращаемся к задаче
        await handle_task_detail(callback)
        
    except Exception as e:
        logger.error("assign_error", error=str(e))
        await callback.answer("❌ Ошибка назначения")


@router.callback_query(F.data.startswith("tasks_project:"))
async def handle_tasks_by_project(callback: CallbackQuery):
    """Показать задачи конкретного проекта."""
    project_id = int(callback.data.split(":")[1])

    try:
        async with AsyncSessionLocal() as session:
            service = TaskService(session)

            if project_id == 0:
                # Без проекта
                tasks = await service.get_all_tasks()
                tasks = [t for t in tasks if not t.project_id]
                header = "📋 Задачи без проекта"
            else:
                from app.repositories.project_repository import ProjectRepository
                repo = ProjectRepository(session)
                project = await repo.get_by_id(project_id)

                if not project:
                    await callback.answer("❌ Проект не найден")
                    return

                tasks = await service.get_all_tasks()
                tasks = [t for t in tasks if t.project_id == project_id]
                emoji = project.emoji or "📁"
                header = f"{emoji} {project.name}"

        if not tasks:
            await callback.message.edit_text(
                f"{header}\n\n✨ Задач нет",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="↩️ К проектам", callback_data="tasks:projects")
                ]])
            )
        else:
            _task_cache[callback.from_user.id] = tasks
            await callback.message.edit_text(
                f"{header} ({len(tasks)})\n\nВыберите задачу:",
                reply_markup=task_buttons_keyboard(tasks, page=0)
            )
        await callback.answer()

    except Exception as e:
        logger.error("tasks_by_project_error", error=str(e))
        await callback.answer("❌ Ошибка")


@router.callback_query(F.data.startswith("unassign:"))
async def handle_unassign(callback: CallbackQuery):
    """Снять исполнителя с задачи."""
    task_id = int(callback.data.split(":")[1])

    try:
        async with AsyncSessionLocal() as session:
            service = TaskService(session)
            task = await service.get_task(task_id)
            if task:
                task.assignee_id = None
                task.assignee_telegram_id = None
                task.assignee_name = None
                await session.commit()

        await callback.answer("✅ Исполнитель снят")
        await handle_task_detail(callback)

    except Exception as e:
        logger.error("unassign_error", error=str(e))
        await callback.answer("❌ Ошибка")
