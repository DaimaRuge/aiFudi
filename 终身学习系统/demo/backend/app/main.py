"""终身学习数字读书系统 - 后端主入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api import auth, documents, knowledge, chat, learning


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 启动成功")
    yield
    # 关闭时清理资源
    print("👋 应用关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## 个人终身学习数字读书系统 MVP

基于大模型 Agent 的智能学习生态系统，实现从信息管理到知识创造，再到个人成长的完整闭环。

### 核心功能
- 📚 **文档管理**：上传、解析 PDF/TXT/DOCX 文档
- 🧠 **知识图谱**：自动构建知识网络
- 💬 **AI 对话**：与文档内容智能对话
- 📈 **学习路径**：个性化学习规划

### 技术栈
- FastAPI + SQLAlchemy
- OpenAI API (或模拟模式)
- SQLite 数据库
    """,
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(knowledge.router)
app.include_router(chat.router)
app.include_router(learning.router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
