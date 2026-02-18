"""Meeting handlers."""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from app.core.db import AsyncSessionLocal
from app.domain.models import Meeting
from app.repositories.meeting_repository import MeetingRepository
from app.core.logging import get_logger

logger = get_logger(__name__)

router = Router()


class MeetingStates(StatesGroup):
    """States for meeting creation."""
    waiting_for_summary = State()


@router.message(Command("meeting"))
async def cmd_meeting(message: Message, state: FSMContext):
    """Handle /meeting command - record meeting summary."""
    await message.answer(
        "📝 Фиксация результатов встречи\n\n"
        "Введите краткое резюме:"
    )
    await state.set_state(MeetingStates.waiting_for_summary)


@router.message(MeetingStates.waiting_for_summary)
async def process_meeting_summary(message: Message, state: FSMContext):
    """Process meeting summary input."""
    
    summary = message.text
    
    async with AsyncSessionLocal() as session:
        repo = MeetingRepository(session)
        
        meeting = Meeting(
            meeting_date=datetime.utcnow(),
            summary=summary
        )
        
        meeting = await repo.create(meeting)
        await session.commit()
    
    await message.answer(
        f"✅ Встреча зафиксирована!\n\n"
        f"📅 {meeting.meeting_date.strftime('%d.%m.%Y %H:%M')}\n"
        f"📝 {meeting.summary}"
    )
    
    await state.clear()
    logger.info("meeting_recorded", meeting_id=meeting.id)


@router.message(Command("meetings"))
async def cmd_meetings_list(message: Message):
    """Show recent meetings."""
    
    async with AsyncSessionLocal() as session:
        repo = MeetingRepository(session)
        meetings = await repo.get_recent(days=30)
    
    if not meetings:
        await message.answer("📋 Встреч за последний месяц не было")
        return
    
    text = "📅 **Последние встречи:**\n\n"
    
    for meeting in meetings:
        date_str = meeting.meeting_date.strftime("%d.%m.%Y")
        text += f"• **{date_str}**\n"
        text += f"  {meeting.summary}\n\n"
    
    await message.answer(text, parse_mode="Markdown")
