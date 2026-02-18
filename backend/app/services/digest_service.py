"""Weekly digest service."""
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models import Task, Meeting
from app.domain.enums import TaskStatus
from app.repositories.task_repository import TaskRepository
from app.repositories.meeting_repository import MeetingRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class DigestService:
    """Service for generating weekly digests."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.task_repo = TaskRepository(session)
        self.meeting_repo = MeetingRepository(session)
    
    async def generate_weekly_digest(self) -> str:
        """Generate weekly digest message for CURRENT week (Mon-Sun)."""
        from app.core.clock import Clock
        
        # Текущая неделя (Пн-Вс)
        now = Clock.now()
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=6, hours=23, minutes=59)
        
        # Задачи текущей недели
        all_tasks = await self.task_repo.get_all()
        week_tasks = [t for t in all_tasks if week_start <= t.created_at <= week_end]
        
        # Встречи текущей недели
        all_meetings = await self.meeting_repo.get_recent(days=30)
        week_meetings = [m for m in all_meetings if week_start <= m.meeting_date <= week_end]
        
        digest = self._build_digest_message(week_tasks, week_meetings, week_start, week_end)
        logger.info("weekly_digest_generated", tasks_count=len(week_tasks))
        
        return digest
    
    def _build_digest_message(
        self,
        tasks: List[Task],
        meetings: List[Meeting],
        week_start: datetime,
        week_end: datetime
    ) -> str:
        """Build formatted digest message."""
        
        # Header
        start_str = week_start.strftime("%d.%m")
        end_str = week_end.strftime("%d.%m.%Y")
        message = (
            f"📊 *Еженедельный дайджест*\n"
            f"📅 {start_str} - {end_str}\n"
            f"_Текущая неделя (Пн-Вс)_\n\n"
        )
        
        # Tasks statistics
        completed = [t for t in tasks if t.status == TaskStatus.DONE.value]
        in_progress = [t for t in tasks if t.status == TaskStatus.DOING.value]
        blocked = [t for t in tasks if t.status == TaskStatus.BLOCKED.value]
        
        message += "*📈 Статистика задач:*\n"
        message += f"  ✅ Выполнено: {len(completed)}\n"
        message += f"  🔄 В работе: {len(in_progress)}\n"
        message += f"  🚫 Заблокировано: {len(blocked)}\n"
        message += f"  📝 Всего за неделю: {len(tasks)}\n\n"
        
        # Completed tasks
        if completed:
            message += "*✅ Выполненные задачи:*\n"
            for task in completed[:5]:
                assignee = f" ({self._format_assignee(task)})" if task.assignee or task.assignee_name else ""
                message += f"  • {task.title}{assignee}\n"
            if len(completed) > 5:
                message += f"  _...и ещё {len(completed) - 5}_\n"
            message += "\n"
        
        # Blocked tasks
        if blocked:
            message += "*⚠️ Заблокированные задачи:*\n"
            for task in blocked:
                message += f"  • {task.title}\n"
                if task.blockers:
                    latest_blocker = task.blockers[-1]
                    message += f"    🚫 {latest_blocker.text}\n"
            message += "\n"
        
        # Meetings
        if meetings:
            message += "*🤝 Встречи на неделе:*\n"
            for meeting in sorted(meetings, key=lambda m: m.meeting_date):
                date_str = meeting.meeting_date.strftime("%d.%m %H:%M")
                # Обрезаем длинные резюме
                summary = meeting.summary[:60] + "..." if len(meeting.summary) > 60 else meeting.summary
                message += f"  • *{date_str}:* {summary}\n"
            message += "\n"
        
        # Team activity
        assignees = {}
        for task in tasks:
            name = self._format_assignee(task)
            if name:
                if name not in assignees:
                    assignees[name] = {'total': 0, 'completed': 0}
                assignees[name]['total'] += 1
                if task.status == TaskStatus.DONE.value:
                    assignees[name]['completed'] += 1
        
        if assignees:
            message += "*👥 Активность команды:*\n"
            for name, stats in sorted(assignees.items(), key=lambda x: x[1]['completed'], reverse=True):
                completion_rate = int(stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
                message += f"  • {name}: {stats['completed']}/{stats['total']} ({completion_rate}%)\n"
            message += "\n"
        
        message += "---\n🎯 Продуктивной недели!"
        
        return message
    
    def _format_assignee(self, task: Task) -> str:
        """Форматируем имя исполнителя без дублирования @."""
        if task.assignee:
            return task.assignee.display_name
        elif task.assignee_name:
            # Убираем @ если он уже есть
            return task.assignee_name if task.assignee_name.startswith('@') else f"@{task.assignee_name}"
        return ""
    
    async def get_overdue_reminder(self) -> str:
        """Get reminder about overdue tasks."""
        from app.core.clock import Clock
        
        all_tasks = await self.task_repo.get_all()
        now = Clock.now()
        
        overdue = [
            t for t in all_tasks
            if t.due_date and t.due_date < now and t.status != TaskStatus.DONE.value
        ]
        
        if not overdue:
            return None
        
        message = "⏰ *Напоминание о просроченных задачах:*\n\n"
        
        for task in overdue:
            days_overdue = (now - task.due_date).days
            assignee = f" ({self._format_assignee(task)})" if task.assignee or task.assignee_name else ""
            message += f"  • {task.title}{assignee}\n"
            message += f"    📅 Просрочено на {days_overdue} дн.\n"
        
        return message
