from typing import AsyncGenerator
import os
import urllib.parse
import ssl

# boto3 imported lazily inside AWS helper to avoid import errors in non-AWS workflows


from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# import models so metadata is available for create_all
from app.models import generated_models as models


# Build DATABASE_URL based on mode. If DATABASE_MODE=aws use RDS IAM auth token
DATABASE_MODE = os.getenv("DATABASE_MODE", "local")

def _build_aws_database_url() -> str:
    # If Docker secrets are used, load them into env vars first
    _load_aws_secrets_from_files()

    import boto3

    region = os.getenv("AWS_REGION")
    host = os.getenv("AWS_DB_HOST")
    port = int(os.getenv("AWS_DB_PORT", "5432"))
    db = os.getenv("AWS_DB_NAME")
    user = os.getenv("AWS_DB_USER")

    # boto3 client will pick up credentials from environment, IAM role, or profile
    rds = boto3.client("rds", region_name=region)
    token = rds.generate_db_auth_token(DBHostname=host, Port=port, DBUsername=user)
    token_quoted = urllib.parse.quote_plus(token)

    # Use asyncpg driver. SSL is configured via create_async_engine(connect_args=...).
    return f"postgresql+asyncpg://{user}:{token_quoted}@{host}:{port}/{db}"


def _load_aws_secrets_from_files() -> None:
    """If Docker secrets or *_FILE env vars are present, load them into process env.

    Expected docker secret paths: /run/secrets/aws_access_key_id, /run/secrets/aws_secret_access_key, /run/secrets/aws_session_token
    Also supports env vars: AWS_ACCESS_KEY_ID_FILE, AWS_SECRET_ACCESS_KEY_FILE, AWS_SESSION_TOKEN_FILE
    """
    secret_map = {
        "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID_FILE") or "/run/secrets/aws_access_key_id",
        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY_FILE") or "/run/secrets/aws_secret_access_key",
        "AWS_SESSION_TOKEN": os.getenv("AWS_SESSION_TOKEN_FILE") or "/run/secrets/aws_session_token",
    }

    for env_name, path in secret_map.items():
        try:
            if path and os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    val = f.read().strip()
                if val:
                    os.environ.setdefault(env_name, val)
        except Exception:
            # silently ignore read errors; boto3 will fall back to other providers
            pass


# Default DATABASE_URL (can be overridden by env var DATABASE_URL)
env_database_url = os.getenv("DATABASE_URL")
if DATABASE_MODE == "aws":
    DATABASE_URL = env_database_url or _build_aws_database_url()
else:
    DATABASE_URL = env_database_url or "postgresql+asyncpg://postgres:postgres@localhost:5432/dicejobmanager"

# support psycopg env var by switching to asyncpg driver
if DATABASE_URL.startswith("postgresql+psycopg"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg", "postgresql+asyncpg", 1)


# Async engine and session factory
connect_args = {}
if DATABASE_MODE == "aws":
    # asyncpg expects SSL in connect args rather than `sslmode` URL params.
    connect_args["ssl"] = ssl.create_default_context()

engine = create_async_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Create tables from models if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
