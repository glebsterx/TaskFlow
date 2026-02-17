"""Database connection and session management."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text, event
from app.config import settings

Base = declarative_base()

def _make_engine():
    """Create engine with proper settings for SQLite."""
    kwargs = {
        "echo": settings.DEBUG,
        "future": True,
    }

    if "sqlite" in settings.DATABASE_URL:
        # NullPool - каждый раз новое соединение, не блокирует между процессами
        from sqlalchemy.pool import NullPool
        kwargs["poolclass"] = NullPool
        kwargs["connect_args"] = {
            "check_same_thread": False,
            "timeout": 10,
        }
    else:
        kwargs["pool_size"] = settings.DB_POOL_SIZE
        kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
        kwargs["pool_pre_ping"] = True

    return create_async_engine(settings.DATABASE_URL, **kwargs)


engine = _make_engine()

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """Dependency for getting database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """Initialize database - create all tables."""
    # Import all models to register them with Base
    from app.domain.models import Task, Blocker, Meeting  # noqa
    from app.domain.user import User  # noqa

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        if "sqlite" in settings.DATABASE_URL:
            await conn.execute(text("PRAGMA journal_mode=WAL"))
            await conn.execute(text("PRAGMA synchronous=NORMAL"))
            await conn.execute(text("PRAGMA cache_size=-64000"))
            await conn.execute(text("PRAGMA temp_store=MEMORY"))
            await conn.execute(text("PRAGMA busy_timeout=5000"))
