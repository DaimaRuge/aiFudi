# SkyOne Shuge 项目初始化

## 快速开始

```bash
# 克隆项目
git clone https://github.com/yourname/skyone-shuge.git
cd skyone-shuge

# 安装依赖
poetry install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 初始化数据库
python scripts/init_db.py

# 运行开发服务器
poetry run uvicorn skyone_shuge.api.main:app --reload

# 运行前端
cd frontend && npm install && npm run dev
```

---

## 项目结构

```
skyone-shuge/
├── skyone_shuge/              # 后端主包
│   ├── __init__.py
│   ├── api/                   # FastAPI 应用
│   │   ├── __init__.py
│   │   ├── main.py           # 应用入口
│   │   ├── deps.py           # 依赖注入
│   │   └── routers/          # API 路由
│   │       ├── __init__.py
│   │       ├── documents.py   # 文档接口
│   │       ├── categories.py # 分类接口
│   │       └── search.py     # 搜索接口
│   │
│   ├── core/                 # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py        # 配置
│   │   ├── database.py      # 数据库连接
│   │   └── security.py      # 安全相关
│   │
│   ├── models/               # 数据模型
│   │   ├── __init__.py
│   │   ├── document.py      # 文档模型
│   │   └── category.py     # 分类模型
│   │
│   ├── services/             # 业务逻辑
│   │   ├── __init__.py
│   │   ├── scanner.py      # 文档扫描
│   │   ├── indexer.py      # 索引管理
│   │   └── classifier.py   # AI 分类
│   │
│   ├── ml/                   # 机器学习
│   │   ├── __init__.py
│   │   ├── embedding.py     # 向量化
│   │   └── llm.py         # LLM 集成
│   │
│   └── utils/                # 工具函数
│       ├── __init__.py
│       ├── file.py         # 文件操作
│       └── hash.py         # 哈希计算
│
├── frontend/                  # 前端项目
│   ├── src/
│   │   ├── components/     # React 组件
│   │   ├── pages/          # 页面
│   │   ├── stores/         # 状态管理
│   │   └── api/            # API 调用
│   └── package.json
│
├── tests/                    # 测试
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   └── integration/
│
├── scripts/                  # 脚本
│   ├── init_db.py
│   └── seed_data.py
│
├── docs/                    # 文档
│   ├── api/
│   └── architecture/
│
├── .env.example
├── pyproject.toml
├── Dockerfile
└── README.md
```

---

## pyproject.toml

```toml
[tool.poetry]
name = "skyone-shuge"
version = "0.1.0"
description = "天一阁 - 智能个人数字文献管理平台"
authors = ["Your Name <your@email.com>"]

[tool.poetry.dependencies]
python = "^3.11"

# Web 框架
fastapi = "^0.109.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}

# 数据库
sqlalchemy = "^2.0.25"
alembic = "^1.13.1"
aiosqlite = "^0.19.0"
redis = "^5.0.1"

# 向量数据库
qdrant-client = "^1.7.0"

# AI
langchain = "^0.1.5"
langchain-openai = "^0.0.8"
langchain-anthropic = "^0.1.0"
sentence-transformers = "^2.2.2"

# 文档处理
pymupdf = "^1.23.0"
python-docx = "^1.1.0"
python-pptx = "^0.6.23"
markdown = "^3.5.2"

# CLI
typer = "^0.9.0"
rich = "^13.7.0"

# 工具
pydantic = "^2.5.3"
pydantic-settings = "^2.1.0"
python-dotenv = "^1.0.0"
aiofiles = "^23.2.1"

# 测试
pytest = "^7.4.4"
pytest-asyncio = "^0.23.3"
httpx = "^0.26.0"

[tool.poetry.group.dev.dependencies]
black = "^23.12.1"
ruff = "^0.1.8"
mypy = "^1.8.0"
pre-commit = "^3.6.0"

[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "UP"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
ignore_missing_imports = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
```

---

## 核心代码示例

### 1. 配置管理 (core/config.py)

```python
from pydantic import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "SkyOne Shuge"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # 数据库
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/skyone.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    
    # 安全
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    
    # AI
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # 文件
    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### 2. 数据库模型 (models/document.py)

```python
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from ..core.database import Base


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True)
    file_path = Column(String(1024), nullable=False)
    file_name = Column(String(512), nullable=False)
    file_hash = Column(String(64), unique=True, nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(100))
    extension = Column(String(20))
    
    # 元数据
    title = Column(String(512))
    authors = Column(ARRAY(Text))
    abstract = Column(Text)
    keywords = Column(ARRAY(Text))
    
    # 分类
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"))
    
    # 状态
    status = Column(String(20), default="pending")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 索引
    __table_args__ = (
        Index("idx_documents_category", "category_id"),
        Index("idx_documents_status", "status"),
        Index("idx_documents_updated", "updated_at"),
    )
```

### 3. API 路由 (routers/documents.py)

```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from ..services.scanner import ScannerService
from ..schemas.document import DocumentCreate, DocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/scan", response_model=dict)
async def scan_documents(
    paths: List[str],
    recursive: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """扫描指定目录"""
    scanner = ScannerService(db)
    task = await scanner.scan(paths, recursive=recursive)
    return {"task_id": task.id, "status": "pending"}


@router.get("", response_model=dict)
async def list_documents(
    page: int = 1,
    limit: int = 20,
    category_id: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取文档列表"""
    from ..services.indexer import IndexerService
    indexer = IndexerService(db)
    result = await indexer.list_documents(
        page=page,
        limit=limit,
        filters={"category_id": category_id, "status": status}
    )
    return result


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    """获取文档详情"""
    from ..services.indexer import IndexerService
    indexer = IndexerService(db)
    doc = await indexer.get_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.put("/{doc_id}")
async def update_document(
    doc_id: str,
    updates: dict,
    db: AsyncSession = Depends(get_db)
):
    """更新文档"""
    from ..services.indexer import IndexerService
    indexer = IndexerService(db)
    success = await indexer.update(doc_id, updates)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document updated"}
```

### 4. 文档扫描服务 (services/scanner.py)

```python
import hashlib
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.document import Document
from ..models.category import Category
from ..utils.file import FileExtractor


class ScannerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.extractor = FileExtractor()
    
    async def scan(
        self,
        paths: List[str],
        recursive: bool = True,
        extensions: Optional[List[str]] = None
    ) -> Dict:
        """扫描目录，返回新发现的文档"""
        
        # 创建扫描任务
        task_id = self._generate_task_id()
        
        # 异步扫描
        asyncio.create_task(self._scan_task(task_id, paths, recursive, extensions))
        
        return {"task_id": task_id, "status": "pending"}
    
    async def _scan_task(
        self,
        task_id: str,
        paths: List[str],
        recursive: bool,
        extensions: Optional[List[str]]
    ):
        """实际执行扫描"""
        
        for base_path in paths:
            path = Path(base_path)
            
            if path.is_file():
                await self._process_file(path)
            elif path.is_dir():
                pattern = "**/*" if recursive else "*"
                for file_path in path.glob(pattern):
                    if file_path.is_file():
                        await self._process_file(file_path)
    
    async def _process_file(self, file_path: Path):
        """处理单个文件"""
        
        # 检查是否支持
        if not self.extractor.is_supported(file_path.suffix):
            return
        
        # 计算哈希
        file_hash = self._compute_hash(file_path)
        
        # 检查是否已存在
        existing = await self._get_by_hash(file_hash)
        if existing:
            return
        
        # 提取元数据
        metadata = await self.extractor.extract(file_path)
        
        # 创建文档记录
        doc = Document(
            id=self._generate_uuid(),
            file_path=str(file_path),
            file_name=file_path.name,
            file_hash=file_hash,
            file_size=file_path.stat().st_size,
            extension=file_path.suffix.lower(),
            file_type=self._get_mime_type(file_path.suffix),
            **metadata
        )
        
        self.db.add(doc)
        await self.db.commit()
    
    def _compute_hash(self, file_path: Path) -> str:
        """计算文件 SHA-256 哈希"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _generate_uuid(self) -> str:
        import uuid
        return str(uuid.uuid4())
    
    def _generate_task_id(self) -> str:
        import uuid
        return f"task_{uuid.uuid4().hex[:8]}"
    
    async def _get_by_hash(self, file_hash: str):
        """根据哈希查找已存在文档"""
        from sqlalchemy import select
        result = await self.db.execute(
            select(Document).where(Document.file_hash == file_hash)
        )
        return result.scalar_one_or_none()
    
    def _get_mime_type(self, extension: str) -> str:
        """获取 MIME 类型"""
        mime_types = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".doc": "application/msword",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".html": "text/html",
        }
        return mime_types.get(extension.lower(), "application/octet-stream")
```

### 5. AI 分类服务 (services/classifier.py)

```python
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.document import Document
from ..models.category import Category


class ClassifierService:
    def __init__(self, db: AsyncSession, llm_provider: str = "openai"):
        self.db = db
        self.llm_provider = llm_provider
    
    async def classify_document(
        self,
        document: Document,
        force: bool = False
    ) -> Dict:
        """对文档进行 AI 分类"""
        
        # 如果已有分类且未强制，重新分类则跳过
        if document.category_id and not force:
            return {"category_id": document.category_id, "cached": True}
        
        # 提取文档特征
        features = self._extract_features(document)
        
        # 获取候选分类
        candidates = await self._get_candidate_categories()
        
        # AI 分类
        result = await self._llm_classify(features, candidates)
        
        return result
    
    async def classify_batch(
        self,
        document_ids: List[str],
        strategy: str = "hybrid"
    ) -> List[Dict]:
        """批量分类"""
        results = []
        
        for doc_id in document_ids:
            doc = await self._get_document(doc_id)
            if doc:
                result = await self.classify_document(doc)
                results.append({"document_id": doc_id, **result})
        
        return results
    
    def _extract_features(self, document: Document) -> Dict:
        """提取文档特征用于分类"""
        return {
            "title": document.title,
            "authors": document.authors,
            "keywords": document.keywords,
            "content_summary": document.abstract[:500] if document.abstract else ""
        }
    
    async def _get_candidate_categories(self) -> List[Dict]:
        """获取候选分类列表"""
        from sqlalchemy import select
        from ..models.category import Category
        
        result = await self.db.execute(select(Category))
        categories = result.scalars().all()
        
        return [
            {
                "id": c.id,
                "name": c.name,
                "path": c.path,
                "type": c.type
            }
            for c in categories
        ]
    
    async def _llm_classify(
        self,
        features: Dict,
        candidates: List[Dict]
    ) -> Dict:
        """使用 LLM 进行分类"""
        
        # 构建提示词
        prompt = self._build_prompt(features, candidates)
        
        # 调用 LLM (示例使用 OpenAI)
        response = await self._call_llm(prompt)
        
        # 解析结果
        result = self._parse_response(response)
        
        return result
    
    def _build_prompt(
        self,
        features: Dict,
        candidates: List[Dict]
    ) -> str:
        """构建分类提示词"""
        
        prompt = f"""请根据以下文档信息，从候选分类中选择最合适的分类。

文档信息:
- 标题: {features.get('title', '未知')}
- 作者: {', '.join(features.get('authors', []) or ['未知'])}
- 关键词: {', '.join(features.get('keywords', []) or ['无'])}
- 摘要: {features.get('content_summary', '无')}

候选分类:
"""
        for cat in candidates:
            prompt += f"- {cat['path']} ({cat['type']})\n"
        
        prompt += """
请返回最合适的分类路径 (JSON 格式):
{"path": "分类路径", "confidence": 0.95}
"""
        return prompt
    
    async def _call_llm(self, prompt: str) -> str:
        """调用 LLM API"""
        # 这里集成 OpenAI/Anthropic/智谱等
        pass
    
    def _parse_response(self, response: str) -> Dict:
        """解析 LLM 返回结果"""
        import json
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"path": None, "confidence": 0}
```

---

## 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行特定测试
pytest tests/unit/test_models.py -v

# 检查覆盖率
pytest --cov=skyone_shuge --cov-report=html
```

---

## 代码规范检查

```bash
# 格式化代码
black skyone_shuge/ tests/
ruff check skyone_shuge/ tests/

# 类型检查
mypy skyone_shuge/

# 检查导入排序
isort --check-only --diff skyone_shuge/ tests/
```

---

## 部署

```bash
# 构建 Docker 镜像
docker build -t skyone-shuge:latest .

# 运行 Docker Compose
docker-compose up -d

# 查看日志
docker-compose logs -f api

# 停止服务
docker-compose down
```

---

**版本**: v0.8
**日期**: 2026-02-03
**主题**: MVP 脚手架代码
