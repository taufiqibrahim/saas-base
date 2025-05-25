import logging
from contextlib import asynccontextmanager
from urllib.parse import quote_plus
from fastapi import FastAPI
from sqlmodel import create_engine, text

from app.core.config import db_settings
from app.utils import run_alembic_migration


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Running startup events...")

    db_type = db_settings.DB_TYPE
    username = db_settings.DB_USER.get_secret_value()
    password = quote_plus(db_settings.DB_PASSWORD.get_secret_value())
    host = db_settings.DB_HOST
    port = db_settings.DB_PORT
    database = db_settings.DB_NAME

    sqlalchemy_uri = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    logger.info(f"DATABASE: Connecting to [{db_type}] at [{host}]...")

    logger.info("DATABASE: Create postgis extension")
    with create_engine(
        sqlalchemy_uri,
        isolation_level="AUTOCOMMIT"
    ).connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))

    logger.info("DATABASE: Run alembic migrations")
    run_alembic_migration(sqlalchemy_uri)

    yield
