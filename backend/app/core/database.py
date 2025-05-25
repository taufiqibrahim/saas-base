from urllib.parse import quote_plus
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import db_settings


username = db_settings.DB_USER.get_secret_value()
password = quote_plus(db_settings.DB_PASSWORD.get_secret_value())
host = db_settings.DB_HOST
port = db_settings.DB_PORT
database = db_settings.DB_NAME
db_path = "db.sqlite3"

if db_settings.DB_TYPE == "sqlite":
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", connect_args={"check_same_thread": False})
elif db_settings.DB_TYPE == "postgres":
    # engine = create_async_engine(f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}", echo=True)
    engine = create_async_engine(f"postgresql+psycopg://{username}:{password}@{host}:{port}/{database}", echo=True)
else:
    raise NotImplementedError(f"DB_TYPE={db_settings.DB_TYPE} not implemented")

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
