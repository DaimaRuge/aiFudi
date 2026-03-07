"""
AI Fudi - Agent 模块

边缘 AI 代理系统
"""

from .openclaw import (
    OpenClawMiddleware,
    DeviceState,
    ErrorCode,
    OpenClawError,
    DeviceConfig,
    AudioConfig,
    ModelConfig,
    Intent,
)

__all__ = [
    "OpenClawMiddleware",
    "DeviceState", 
    "ErrorCode",
    "OpenClawError",
    "DeviceConfig",
    "AudioConfig",
    "ModelConfig",
    "Intent",
]

__version__ = "0.2.0"
