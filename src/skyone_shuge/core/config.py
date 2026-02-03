"""
天一阁 - 核心配置
"""

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache
import os


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    APP_NAME: str = "SkyOne Shuge"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API 配置
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/skyone.db"
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Qdrant 配置
    QDRANT_URL: str = "http://localhost:6333"
    
    # AI 配置
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    
    # Embedding 模型
    EMBEDDING_MODEL: str = "BAAI/bge-large-zh"
    EMBEDDING_DEVICE: str = "cpu"
    
    # 文件配置
    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB
    
    # 支持的文件扩展名
    ALLOWED_EXTENSIONS: List[str] = [
        ".pdf", ".docx", ".doc", ".xlsx", ".xls",
        ".pptx", ".ppt", ".txt", ".md", ".html",
        ".epub", ".fb2", ".mobi"
    ]
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例"""
    return Settings()


settings = get_settings()
