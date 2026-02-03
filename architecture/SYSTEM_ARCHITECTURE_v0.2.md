# SkyOne Shuge 架构设计 v0.2

## 目录

1. [系统架构总览](#1-系统架构总览)
2. [核心模块详解](#2-核心模块详解)
3. [数据模型设计](#3-数据模型设计)
4. [API 接口规范](#4-api-接口规范)
5. [大模型集成方案](#5-大模型集成方案)
6. [部署架构](#6-部署架构)
7. [安全与隐私](#7-安全与隐私)
8. [性能优化](#8-性能优化)

---

## 1. 系统架构总览

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            SkyOne Shuge                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                       接入层 (Presentation)                     │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │    │
│  │  │   Web     │  │  Desktop  │  │   CLI     │  │   API     │   │    │
│  │  │  React    │  │ Tauri     │  │  Rust     │  │ FastAPI   │   │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                       应用服务层 (Application)                   │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐  │    │
│  │  │  文档扫描   │ │  索引管理   │ │  分类引擎   │ │  同步服务   │  │    │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                       AI 能力层 (AI Engine)                      │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐  │    │
│  │  │  文本向量   │ │  RAG 检索   │ │  Agent     │ │  文本生成   │  │    │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                       数据持久层 (Data)                          │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │    │
│  │  │  SQLite    │ │ PostgreSQL │ │   Redis    │ │  Qdrant    │   │    │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 技术栈矩阵

| 层级 | 技术选型 | 用途 |
|-----|---------|------|
| 后端框架 | FastAPI | API 服务 |
| CLI 框架 | Typer/Clap | 命令行工具 |
| 数据库 (端侧) | SQLite | 本地数据 |
| 数据库 (云端) | PostgreSQL | 云端数据 |
| 向量数据库 | Qdrant | 语义检索 |
| 缓存 | Redis | 缓存/队列 |
| 前端框架 | React | Web UI |
| 桌面框架 | Tauri | 桌面应用 |
| LLM 框架 | LangChain/LlamaIndex | AI 编排 |
| 向量模型 | BGE/M3E | 文本向量化 |
| OCR | PaddleOCR | 文字识别 |
| 文档解析 | Apache Tika | 文档解析 |

---

## 2. 核心模块详解

### 2.1 文档扫描器

```python
class DocumentScanner:
    async def scan(
        self,
        paths: List[str],
        recursive: bool = True,
        patterns: Optional[List[str]] = None
    ) -> ScanResult:
        """扫描目录，返回文档列表"""
        pass
    
    async def watch(
        self,
        paths: List[str],
        callback: Callable[[FileChangeEvent], None]
    ) -> None:
        """实时监控文件变化"""
        pass
```

### 2.2 索引管理器

```python
class IndexManager:
    async def add_document(
        self,
        document: Document,
        skip_vectorize: bool = False
    ) -> str:
        """添加文档到索引"""
        pass
    
    async def search(
        self,
        query: SearchQuery,
        limit: int = 20,
        offset: int = 0
    ) -> SearchResult:
        """搜索文档 (混合搜索: 关键词 + 向量)"""
        pass
```

### 2.3 分类引擎

```python
class Classifier:
    async def classify(
        self,
        document: Document,
        force: bool = False
    ) -> ClassificationResult:
        """对文档进行分类"""
        pass
```

### 2.4 同步服务

```python
class SyncService:
    async def push_changes(self) -> SyncResult:
        """推送本地变更到云端"""
        pass
    
    async def pull_changes(self) -> SyncResult:
        """从云端拉取变更"""
        pass
```

### 2.5 AI 编排器

```python
class AgentOrchestrator:
    async def execute(
        self,
        task: str,
        context: Optional[Dict] = None
    ) -> AgentResult:
        """执行 AI 任务 (规划 + 执行 + 综合)"""
        pass
```

---

## 3. 数据模型设计

### 3.1 核心表 (PostgreSQL)

```sql
-- 文档主表
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_hash TEXT UNIQUE NOT NULL,
    file_size BIGINT,
    title TEXT,
    authors TEXT[],
    abstract TEXT,
    keywords TEXT[],
    category_id UUID,
    status TEXT DEFAULT 'pending',
    custom_name TEXT,
    sync_status TEXT DEFAULT 'synced',
    sync_version INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 分类表
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    parent_id UUID,
    path TEXT NOT NULL UNIQUE,
    type TEXT DEFAULT 'user',
    description TEXT,
    rules JSONB
);

-- 项目表
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',
    owner_id UUID NOT NULL,
    settings JSONB DEFAULT '{}'
);

-- 同步日志表
CREATE TABLE sync_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL,
    operation TEXT NOT NULL,
    record_id UUID,
    payload JSONB,
    timestamp TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'pending'
);
```

### 3.2 向量数据库 (Qdrant)

```python
# 集合: documents (维度 1024, Cosine 距离)
# 有效载荷: document_id, content, page, metadata

client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
)
```

---

## 4. API 接口规范

### 4.1 接口列表

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/v1/documents/scan | 扫描目录 |
| GET | /api/v1/documents | 获取文档列表 |
| GET | /api/v1/documents/{id} | 获取文档详情 |
| PUT | /api/v1/documents/{id} | 更新文档 |
| DELETE | /api/v1/documents/{id} | 删除文档 |
| POST | /api/v1/documents/{id}/classify | AI 分类 |
| GET | /api/v1/categories | 获取分类树 |
| POST | /api/v1/sync/push | 推送变更 |
| POST | /api/v1/sync/pull | 拉取变更 |
| POST | /api/v1/ai/search | 语义搜索 |
| POST | /api/v1/ai/generate | AI 内容生成 |

---

## 5. 大模型集成方案

### 5.1 支持的模型

```python
LLM_PROVIDERS = {
    "openai": {"models": ["gpt-4", "gpt-4-turbo"]},
    "anthropic": {"models": ["claude-3-opus", "claude-3-sonnet"]},
    "google": {"models": ["gemini-pro"]},
    "minimax": {"models": ["minimax-01"]},
    "baidu": {"models": ["ernie-4.0"]},
    "alibaba": {"models": ["qwen-turbo", "qwen-plus"]},
    "zhipu": {"models": ["glm-4"]},
}
```

### 5.2 功能映射

| 功能 | 推荐模型 |
|-----|---------|
| 文档分类 | GPT-4 / Claude 3 |
| 元数据提取 | Qwen-Plus / GPT-3.5 |
| 知识问答 | Claude 3 / GPT-4 |
| 内容生成 | GPT-4 / Claude 3 |
| 代码生成 | Claude 3 / Qwen-Plus |

---

## 6. 部署架构

### 6.1 Docker Compose

```yaml
services:
  api:
    build: ./api
    ports: ["8080:8080"]
    depends_on: [postgres, redis, qdrant]
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/skyone
      - REDIS_URL=redis://redis:6379
      - QDRANT_URL=qdrant:6333

  postgres:
    image: postgres:15
    volumes: [postgres_data:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine

  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333"]

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
```

---

## 7. 性能指标

| 指标 | 目标值 |
|-----|-------|
| 文档扫描速度 | > 100 文件/秒 |
| 索引查询延迟 | < 100ms (P95) |
| 同步延迟 | < 1 秒 |
| 搜索延迟 | < 200ms |
| 内存占用 | < 500MB (空闲) |

---

**版本**: v0.2
**更新日期**: 2026-02-03
