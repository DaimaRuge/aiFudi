#!/usr/bin/env python3
"""
AI Fudi - Fudi VoiceOS 主入口

混合AI语音助手框架

核心功能:
- 全双工语音交互
- 云端LLM + 端侧SLM 混合推理
- Super Gateway Agent Orchestrator
"""

__version__ = "0.1.0"
__author__ = "AI Assistant"

from .gateway.super_gateway import SuperGateway
from .core.llm.router import LLMRouter

__all__ = ["SuperGateway", "LLMRouter", "__version__"]
