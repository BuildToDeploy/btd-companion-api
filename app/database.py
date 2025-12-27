from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class DatabaseManager:
    def __init__(self):
        self.settings = get_settings()
        self.engine = None
        self.AsyncSessionLocal = None

    async def init(self):
        """Initialize database engine and session factory"""
        self.engine = create_async_engine(
            self.settings.database_url,
            echo=self.settings.debug,
            pool_size=20,
            max_overflow=10,
        )
        self.AsyncSessionLocal = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        logger.info("Database engine initialized")

    async def close(self):
        """Close database engine"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database engine closed")

    async def get_session(self) -> AsyncSession:
        """Get database session"""
        async with self.AsyncSessionLocal() as session:
            yield session


db_manager = DatabaseManager()
