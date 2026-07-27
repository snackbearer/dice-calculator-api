from typing import AsyncGenerator
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# import models so metadata is available for create_all
from app.models import generated_models as models

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/dicejobmanager")
# support psycopg env var by switching to asyncpg driver
if DATABASE_URL.startswith("postgresql+psycopg"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg", "postgresql+asyncpg", 1)

# Async engine and session factory
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def init_db() -> None:
    """Create tables from models if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
