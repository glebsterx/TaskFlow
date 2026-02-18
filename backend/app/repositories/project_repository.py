"""Project repository."""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models import Project


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_active(self) -> List[Project]:
        result = await self.session.execute(
            select(Project)
            .where(Project.is_active == True)
            .order_by(Project.name)
        )
        return list(result.scalars().all())

    async def get_by_id(self, project_id: int) -> Optional[Project]:
        result = await self.session.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def create(self, name: str, description: str = None, emoji: str = "📁") -> Project:
        project = Project(name=name, description=description, emoji=emoji)
        self.session.add(project)
        await self.session.flush()
        return project
