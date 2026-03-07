"""
AI Fudi - Logging

结构化日志配置
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from .config import settings


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    format_str: Optional[str] = None
) -> logging.Logger:
    """
    配置日志系统
    
    Args:
        level: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        log_file: 日志文件路径
        format_str: 日志格式
        
    Returns:
        Logger: 配置好的 logger
    """
    # 使用配置或默认值
    level = level or settings.logging.level
    log_file = log_file or settings.logging.file
    format_str = format_str or settings.logging.format
    
    # 创建 logger
    logger = logging.getLogger("aifudi")
    logger.setLevel(getattr(logging, level))
    logger.handlers = []  # 清除现有 handlers
    
    # 格式化器
    formatter = logging.Formatter(format_str)
    
    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件 handler (如果配置了)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(getattr(logging, level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取命名 logger
    
    Args:
        name: logger 名称 (如 "aifudi.agents.openclaw")
        
    Returns:
        Logger: 命名 logger
    """
    return logging.getLogger(f"aifudi.{name}")


# 全局 logger
logger = setup_logging()
