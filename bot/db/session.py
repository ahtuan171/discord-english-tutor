from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot import config
from bot.db.models import Base

# Supabase's pooler runs PgBouncer in transaction mode, which is incompatible
# with asyncpg's server-side prepared statements. Disabling the statement
# cache makes every query a plain (unprepared) query instead.
engine = create_async_engine(
    config.DATABASE_URL,
    echo=False,
    connect_args={"statement_cache_size": 0},
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def get_session():
    async with SessionLocal() as session:
        yield session
