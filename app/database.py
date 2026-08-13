from functools import lru_cache
from typing import AsyncGenerator
import os
import ssl
import logging

# boto3 imported lazily inside AWS helper to avoid import errors in non-AWS workflows


from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

# import models so metadata is available for create_all
from app.models import generated_models as models


logger = logging.getLogger(__name__)


# Build DATABASE_URL based on mode. If DATABASE_MODE=aws use RDS IAM auth token
DATABASE_MODE = os.getenv("DATABASE_MODE", "local").strip().lower()


def _is_truthy(value: str | None) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _get_aws_db_settings() -> tuple[str, int, str, str]:
    region = os.getenv("AWS_REGION")
    host = os.getenv("AWS_DB_HOST")
    db = os.getenv("AWS_DB_NAME")
    user = os.getenv("AWS_DB_USER")
    port = int(os.getenv("AWS_DB_PORT", "5432"))

    missing = [
        name
        for name, value in {
            "AWS_REGION": region,
            "AWS_DB_HOST": host,
            "AWS_DB_NAME": db,
            "AWS_DB_USER": user,
        }.items()
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing required AWS database settings: {', '.join(missing)}")

    return host, port, db, user


@lru_cache(maxsize=1)
def _get_ssl_context() -> ssl.SSLContext:
    return ssl.create_default_context()


@lru_cache(maxsize=1)
def _get_rds_client():
    _load_aws_secrets_from_files()
    import boto3

    region = os.getenv("AWS_REGION")
    return boto3.client("rds", region_name=region)


def _generate_aws_iam_auth_token(host: str, port: int, user: str) -> str:
    # Token is short-lived and must be refreshed whenever a new physical connection is created.
    return _get_rds_client().generate_db_auth_token(
        DBHostname=host,
        Port=port,
        DBUsername=user,
    )

def _build_aws_database_url() -> str:
    host, port, db, user = _get_aws_db_settings()
    # Password/token is injected per new connection via SQLAlchemy events.
    return f"postgresql+asyncpg://{user}@{host}:{port}/{db}"


def configure_aws_iam_auth(sync_engine: Engine) -> None:
    if DATABASE_MODE != "aws":
        return

    host, port, _, user = _get_aws_db_settings()

    @event.listens_for(sync_engine, "do_connect")
    def _inject_fresh_iam_token(dialect, conn_rec, cargs, cparams):
        cparams["host"] = host
        cparams["port"] = port
        cparams["user"] = user
        cparams["password"] = _generate_aws_iam_auth_token(host=host, port=port, user=user)
        cparams["ssl"] = _get_ssl_context()

        # Intentionally avoid logging auth tokens.
        logger.debug("Generated fresh IAM auth token for new PostgreSQL connection")


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
    connect_args["ssl"] = _get_ssl_context()

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
    pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
    # Recycle idle pooled connections periodically to reduce stale socket risk.
    pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "1800")),
)

configure_aws_iam_auth(engine.sync_engine)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Create tables from models if they do not exist."""
    if DATABASE_MODE == "aws":
        return
    if not _is_truthy(os.getenv("LOCAL_DB_AUTO_CREATE", "true")):
        return

    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
