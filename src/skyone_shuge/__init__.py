#!/usr/bin/env python3
"""
天一阁 - SkyOne Shuge
智能个人数字文献管理平台

一个基于 AI 的智能知识管理系统，帮助用户管理、分类、搜索和分析数字文献。

功能特性:
- 📄 文档管理与索引
- 🤖 AI 自动分类 (GPT-4, Claude)
- 🔍 语义搜索 (向量数据库)
- 🏷️ 智能标签系统
- 👤 用户认证
- 📱 跨平台支持

作者: AI Assistant
版本: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"

from .api.main import app
from .core.config import settings

__all__ = ["app", "settings", "__version__"]
