#!/usr/bin/env python3
"""
SkyOne Shuge - 数据库初始化脚本
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from skyone_shuge.core.database import init_db
from skyone_shuge.core.config import settings


def main():
    """初始化数据库"""
    
    print(f"🚀 初始化 {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📁 数据库: {settings.DATABASE_URL}")
    print()
    
    # 初始化
    init_db()
    
    print()
    print("✅ 数据库初始化完成!")
    print()
    print("下一步:")
    print("  1. 运行开发服务器: poetry run uvicorn skyone_shuge.api.main:app --reload")
    print("  2. 访问: http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    main()
