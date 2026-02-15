"""Weekly digest service for sending summaries."""
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
        """Generate weekly digest message."""
        
        # Get week boundaries
        now = datetime.utcnow()
        week_start = now - timedelta(days=now.weekday() + 7)  # Last Monday
        week_end = week_start + timedelta(days=7)
        
        # Get tasks
        all_tasks = await self.task_repo.get_all()
        week_tasks = [t for t in all_tasks if week_start <= t.created_at <= week_end]
        
        # Get meetings
        meetings = await self.meeting_repo.get_recent(days=7)
        
        # Build digest
        digest = self._build_digest_message(week_tasks, meetings, week_start, week_end)
        
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
        message = f"📊 **Еженедельный дайджест**\n"
        message += f"📅 {start_str} - {end_str}\n\n"
        
        # Tasks statistics
        completed = [t for t in tasks if t.status == TaskStatus.DONE.value]
        in_progress = [t for t in tasks if t.status == TaskStatus.DOING.value]
        blocked = [t for t in tasks if t.status == TaskStatus.BLOCKED.value]
        
        message += "**📈 Статистика задач:**\n"
        message += f"  ✅ Выполнено: {len(completed)}\n"
        message += f"  🔄 В работе: {len(in_progress)}\n"
        message += f"  🚫 Заблокировано: {len(blocked)}\n"
        message += f"  📝 Всего: {len(tasks)}\n\n"
        
        # Completed tasks
        if completed:
            message += "**✅ Выполненные задачи:**\n"
            for task in completed[:5]:  # Top 5
                assignee = f" (@{task.assignee_name})" if task.assignee_name else ""
                message += f"  • {task.title}{assignee}\n"
            if len(completed) > 5:
                message += f"  ... и ещё {len(completed) - 5}\n"
            message += "\n"
        
        # Blocked tasks (important!)
        if blocked:
            message += "**⚠️ Заблокированные задачи:**\n"
            for task in blocked:
                message += f"  • {task.title}\n"
                if task.blockers:
                    latest_blocker = task.blockers[-1]
                    message += f"    🚫 {latest_blocker.text}\n"
            message += "\n"
        
        # Meetings
        if meetings:
            message += "**🤝 Встречи:**\n"
            for meeting in meetings:
                date_str = meeting.meeting_date.strftime("%d.%m")
                message += f"  • **{date_str}:** {meeting.summary}\n"
            message += "\n"
        
        # Team members activity
        assignees = {}
        for task in tasks:
            if task.assignee_name:
                if task.assignee_name not in assignees:
                    assignees[task.assignee_name] = {
                        'total': 0,
                        'completed': 0
                    }
                assignees[task.assignee_name]['total'] += 1
                if task.status == TaskStatus.DONE.value:
                    assignees[task.assignee_name]['completed'] += 1
        
        if assignees:
            message += "**👥 Активность команды:**\n"
            for name, stats in sorted(assignees.items(), key=lambda x: x[1]['completed'], reverse=True):
                completion_rate = int(stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
                message += f"  • @{name}: {stats['completed']}/{stats['total']} ({completion_rate}%)\n"
            message += "\n"
        
        # Footer
        message += "---\n"
        message += "🎯 Продуктивной недели!\n"
        
        return message
    
    async def get_overdue_reminder(self) -> str:
        """Get reminder about overdue tasks."""
        
        all_tasks = await self.task_repo.get_all()
        now = datetime.utcnow()
        
        overdue = []
        for task in all_tasks:
            if (task.due_date and 
                task.due_date < now and 
                task.status != TaskStatus.DONE.value):
                overdue.append(task)
        
        if not overdue:
            return None
        
        message = "⏰ **Напоминание о просроченных задачах:**\n\n"
        
        for task in overdue:
            days_overdue = (now - task.due_date).days
            assignee = f" (@{task.assignee_name})" if task.assignee_name else ""
            message += f"  • {task.title}{assignee}\n"
            message += f"    📅 Просрочено на {days_overdue} дн.\n"
        
        return message
