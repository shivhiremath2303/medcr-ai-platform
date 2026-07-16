import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Base class for SQLAlchemy models
Base = declarative_base()

# --- Connection Pooling & Scalability (10.3.6) ---
# Preparing for distributed DB with proper pooling parameters.
# In production, this would point to a PostgreSQL URL via settings.
DB_URL = settings.database_url or "sqlite+aiosqlite:///./data/legal_ai.db"

engine_kwargs = {
    "pool_recycle": 3600,
    "echo": settings.database_echo,
}

# SQLite dialect doesn't support pool_size or max_overflow
if not DB_URL.startswith("sqlite"):
    engine_kwargs["pool_size"] = settings.database_pool_size
    engine_kwargs["max_overflow"] = settings.database_max_overflow

engine = create_async_engine(DB_URL, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for retrieving a database session.
    Ensures sessions are properly closed and pooled.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_database():
    """Initialize database schemas."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("SQL database schema initialized.")
