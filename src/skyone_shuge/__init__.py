"""
天一阁 - SkyOne Shuge

一个现代化的个人知识库管理系统
"""

__version__ = "3.0.1"
__author__ = "SkyOne Shuge Team"

from .core.config import settings, get_settings
from .core.database import Base, engine, init_db, get_db, AsyncSessionLocal

__all__ = [
    "settings",
    "get_settings",
    "Base",
    "engine",
    "init_db",
    "get_db",
    "AsyncSessionLocal",
]
