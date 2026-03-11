"""
天一阁 - 数据库连接 (SQLAlchemy 2.0 异步)
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings
import logging

logger = logging.getLogger(__name__)

# 异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# 声明基类
Base = declarative_base()


async def init_db():
    """初始化数据库 - 创建所有表"""
    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✓ 数据库表创建完成")


async def get_db() -> AsyncSession:
    """获取数据库会话 (依赖注入用)"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"数据库会话错误: {e}")
            raise
        finally:
            await session.close()


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
    logger.info("✓ 数据库连接已关闭")
