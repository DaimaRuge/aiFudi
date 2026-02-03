"""
天一阁 - 数据库连接
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# 同步引擎
SYNC_ENGINE = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True
)

# 异步引擎
ASYNC_ENGINE = create_async_engine(
    settings.DATABASE_URL.replace("sqlite", "sqlite+aiosqlite"),
    echo=settings.DEBUG
)

# 会话工厂
SessionLocal = sessionmaker(
    bind=SYNC_ENGINE,
    autocommit=False,
    autoflush=False
)

AsyncSessionLocal = async_sessionmaker(
    bind=ASYNC_ENGINE,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# 声明基类
Base = declarative_base()


def init_db():
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=SYNC_ENGINE)
    
    # 确保 uploads 目录存在
    from pathlib import Path
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    
    print("✓ 数据库初始化完成")


def get_db():
    """获取数据库会话 (同步)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """获取数据库会话 (异步)"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
