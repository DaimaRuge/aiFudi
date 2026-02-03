# SkyOne Shuge 数据库详细设计 v0.5

## 1. 数据库架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                      SkyOne Shuge 数据库架构                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   SQLite (端侧)                          │   │
│  │  - documents (文档主表)                                  │   │
│  │  - categories (分类表)                                   │   │
│  │  - tags (标签表)                                         │   │
│  │  - projects (项目表)                                     │   │
│  │  - sync_logs (同步日志)                                  │   │
│  │  - user_configs (用户配置)                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   Qdrant (向量库)                        │   │
│  │  - documents (文档向量)                                  │   │
│  │  - categories (分类向量)                                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. SQLite 表结构详细设计

### 2.1 documents (文档主表)

```sql
-- 文档主表
CREATE TABLE documents (
    -- 核心标识
    id TEXT PRIMARY KEY,                    -- UUID (PK)
    
    -- 文件信息
    file_path TEXT NOT NULL,                -- 原始文件路径
    file_name TEXT NOT NULL,                -- 文件名
    file_hash TEXT UNIQUE NOT NULL,         -- SHA-256 文件哈希 (去重)
    file_size BIGINT,                       -- 文件大小 (字节)
    file_type TEXT,                         -- MIME 类型
    extension TEXT,                         -- 文件扩展名 (小写)
    
    -- 元数据 - 基础信息
    title TEXT,                             -- 标题
    subtitle TEXT,                          -- 副标题
    authors TEXT[],                         -- 作者列表 (JSON 数组)
    
    -- 元数据 - 出版信息
    publisher TEXT,                         -- 出版社
    published_date DATE,                    -- 出版日期
    isbn TEXT,                              -- ISBN 号
    doi TEXT,                               -- DOI 号
    volume TEXT,                            -- 卷
    issue TEXT,                             -- 期
    pages TEXT,                             -- 页码 (如 "1-20")
    
    -- 元数据 - 内容信息
    abstract TEXT,                          -- 摘要
    keywords TEXT[],                        -- 关键词 (JSON 数组)
    language TEXT,                          -- 语言 (zh/en)
    content_text TEXT,                      -- 纯文本内容 (用于搜索)
    
    -- 分类信息
    category_id TEXT,                       -- 分类 ID (FK)
    category_path TEXT,                     -- 分类路径 (冗余, 如 "/计算机/AI/机器学习")
    
    -- 用户标记
    tags TEXT[],                            -- 用户标签 (JSON 数组)
    status TEXT DEFAULT 'pending',          -- pending/classified/archived
    rating SMALLINT CHECK (rating BETWEEN 1 AND 5),  -- 星级评分
    
    -- 自定义命名 (LibIndex 核心功能)
    custom_name TEXT,                        -- 自定义名称
    custom编号 TEXT,                         -- 自定义编号 (如 "C001-2024-001")
    
    -- 索引信息
    indexed_at TIMESTAMP,                   -- 最后索引时间
    full_text_indexed BOOLEAN DEFAULT FALSE,-- 是否已全文索引
    content_hash TEXT,                      -- 内容哈希 (检测内容变更)
    
    -- 同步信息
    sync_status TEXT DEFAULT 'synced',       -- synced/pending/error
    sync_version INTEGER DEFAULT 0,          -- 同步版本号
    last_synced_at TIMESTAMP,               -- 最后同步时间
    device_id TEXT,                         -- 来源设备 ID
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,                   -- 软删除时间
    
    -- 约束
    CONSTRAINT fk_category FOREIGN KEY (category_id)
        REFERENCES categories(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_documents_category ON documents(category_id);
CREATE INDEX idx_documents_hash ON documents(file_hash);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_updated ON documents(updated_at DESC);
CREATE INDEX idx_documents_type ON documents(extension);
CREATE INDEX idx_documents_tags ON documents USING GIN(tags);
CREATE INDEX idx_documents_authors ON documents USING GIN(authors);
CREATE INDEX idx_documents_keywords ON documents USING GIN(keywords);

-- 全文搜索索引
CREATE VIRTUAL TABLE documents_fts USING fts5(
    title,
    authors,
    abstract,
    content_text,
    content=documents,
    content_rowid=id
);

-- 触发器 (更新时间)
CREATE TRIGGER documents_update_trigger
    AFTER UPDATE ON documents
BEGIN
    UPDATE documents SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

### 2.2 categories (分类表)

```sql
-- 分类表
CREATE TABLE categories (
    -- 核心标识
    id TEXT PRIMARY KEY,                    -- UUID (PK)
    
    -- 基本信息
    name TEXT NOT NULL,                     -- 分类名称
    parent_id TEXT,                          -- 父分类 ID (FK, 可为空表示顶级)
    path TEXT NOT NULL UNIQUE,               -- 分类路径 (如 "/计算机/AI/机器学习")
    
    -- 分类属性
    type TEXT DEFAULT 'user',                -- system (系统预设) / user (用户创建) / project (项目分类)
    description TEXT,                        -- 分类描述
    color TEXT,                              -- UI 显示颜色 (十六进制)
    icon TEXT,                               -- 图标名称
    sort_order INTEGER DEFAULT 0,            -- 排序顺序
    
    -- 自动分类规则
    rules JSONB DEFAULT '{}',               -- AI 自动分类规则
    -- {
    --   "keywords": ["机器学习", "深度学习"],
    --   "patterns": ["*.pdf"],
    --   "auto_apply": true
    -- }
    
    -- 统计信息
    document_count INTEGER DEFAULT 0,         -- 文档数量
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 约束
    CONSTRAINT fk_parent FOREIGN KEY (parent_id)
        REFERENCES categories(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_categories_parent ON categories(parent_id);
CREATE INDEX idx_categories_type ON categories(type);
CREATE INDEX idx_categories_path ON categories(path);
```

### 2.3 tags (标签表)

```sql
-- 标签表
CREATE TABLE tags (
    id TEXT PRIMARY KEY,                    -- UUID (PK)
    name TEXT UNIQUE NOT NULL,              -- 标签名称 (唯一)
    color TEXT,                              -- 标签颜色
    description TEXT,                        -- 标签描述
    usage_count INTEGER DEFAULT 0,           -- 使用次数
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 文档-标签关联表 (多对多)
CREATE TABLE document_tags (
    document_id TEXT NOT NULL,              -- 文档 ID (FK)
    tag_id TEXT NOT NULL,                   -- 标签 ID (FK)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (document_id, tag_id),
    
    CONSTRAINT fk_document FOREIGN KEY (document_id)
        REFERENCES documents(id) ON DELETE CASCADE,
    CONSTRAINT fk_tag FOREIGN KEY (tag_id)
        REFERENCES tags(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_document_tags_document ON document_tags(document_id);
CREATE INDEX idx_document_tags_tag ON document_tags(tag_id);
```

### 2.4 projects (项目表)

```sql
-- 项目表
CREATE TABLE projects (
    -- 核心标识
    id TEXT PRIMARY KEY,                    -- UUID (PK)
    
    -- 基本信息
    name TEXT NOT NULL,                     -- 项目名称
    description TEXT,                       -- 项目描述
    status TEXT DEFAULT 'active',            -- active/completed/archived
    
    -- 时间范围
    start_date DATE,                         -- 开始日期
    end_date DATE,                           -- 结束日期
    
    -- 所有者
    owner_id TEXT NOT NULL,                  -- 所有者 ID
    
    -- 项目配置
    settings JSONB DEFAULT '{}',             -- 项目配置
    -- {
    --   "default_category": "xxx",
    --   "sync_enabled": true,
    --   "permissions": {...}
    -- }
    
    -- 统计
    document_count INTEGER DEFAULT 0,         -- 文档数量
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_projects_owner ON projects(owner_id);
CREATE INDEX idx_projects_status ON projects(status);

-- 项目-文档关联表
CREATE TABLE project_documents (
    project_id TEXT NOT NULL,               -- 项目 ID (FK)
    document_id TEXT NOT NULL,               -- 文档 ID (FK)
    role TEXT DEFAULT 'reference',           -- primary (主要文档) / reference (参考) / derived (派生)
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (project_id, document_id),
    
    CONSTRAINT fk_project FOREIGN KEY (project_id)
        REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_project_document FOREIGN KEY (document_id)
        REFERENCES documents(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_project_documents_project ON project_documents(project_id);
CREATE INDEX idx_project_documents_document ON project_documents(document_id);
```

### 2.5 devices (设备表)

```sql
-- 设备表
CREATE TABLE devices (
    id TEXT PRIMARY KEY,                    -- UUID (PK)
    name TEXT NOT NULL,                     -- 设备名称
    type TEXT,                               -- desktop / mobile / server
    platform TEXT,                           -- windows / macos / linux / android / ios
    last_seen_at TIMESTAMP,                  -- 最后在线时间
    sync_enabled BOOLEAN DEFAULT TRUE,       -- 同步是否启用
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.6 sync_logs (同步日志表)

```sql
-- 同步日志表
CREATE TABLE sync_logs (
    -- 核心标识
    id TEXT PRIMARY KEY,                    -- UUID (PK)
    
    -- 同步信息
    device_id TEXT NOT NULL,                -- 设备 ID (FK)
    operation TEXT NOT NULL,                -- 操作类型: create / update / delete
    table_name TEXT,                         -- 表名
    record_id TEXT,                          -- 记录 ID
    
    -- 变更数据
    payload JSONB,                           -- 变更数据
    -- {
    --   "before": {...},
    --   "after": {...}
    -- }
    
    -- 同步状态
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending',           -- pending / synced / failed / conflict
    error_message TEXT,                      -- 错误信息
    resolved_at TIMESTAMP,                   -- 解决时间
    
    -- 冲突解决
    resolution TEXT,                         -- 解决方式: keep_local / keep_remote / merge
    resolved_by TEXT,                        -- 解决者 (user / system)
    
    -- 设备标识
    sync_version INTEGER DEFAULT 0           -- 同步版本
);

-- 索引
CREATE INDEX idx_sync_logs_device ON sync_logs(device_id);
CREATE INDEX idx_sync_logs_timestamp ON sync_logs(timestamp DESC);
CREATE INDEX idx_sync_logs_status ON sync_logs(status);
CREATE INDEX idx_sync_logs_operation ON sync_logs(operation);
```

### 2.7 user_configs (用户配置表)

```sql
-- 用户配置表
CREATE TABLE user_configs (
    key TEXT PRIMARY KEY,                    -- 配置键 (PK)
    value JSONB NOT NULL,                   -- 配置值
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 常用配置
INSERT INTO user_configs (key, value) VALUES
('scan.directories', '["~/Documents", "~/Downloads"]'),
('scan.exclude_patterns', '["*.tmp", "*.log", "node_modules"]'),
('naming.template', '{category}/{title}_{year}'),
('classification.auto_apply', 'true'),
('llm.provider', '"openai"'),
('sync.enabled', 'true');
```

### 2.8 classification_history (分类历史表)

```sql
-- 分类历史表 (记录分类变更)
CREATE TABLE classification_history (
    id TEXT PRIMARY KEY,                    -- UUID (PK)
    document_id TEXT NOT NULL,              -- 文档 ID
    old_category_id TEXT,                   -- 原分类 ID
    new_category_id TEXT,                   -- 新分类 ID
    
    -- 分类来源
    source TEXT,                             -- ai / user / import
    confidence REAL,                         -- AI 置信度
    
    -- 操作信息
    operated_by TEXT,                        -- 操作者 (user_id / system)
    operated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT                               -- 备注
    
    CONSTRAINT fk_document FOREIGN KEY (document_id)
        REFERENCES documents(id) ON DELETE CASCADE
);

CREATE INDEX idx_classification_history_document ON classification_history(document_id);
CREATE INDEX idx_classification_history_time ON classification_history(operated_at DESC);
```

---

## 3. 向量数据库设计 (Qdrant)

### 3.1 文档向量集合

```python
# collection: documents
# 向量维度: 1024 (BGE-large-zh)
# 距离度量: Cosine

collection_config = {
    "name": "documents",
    "vector_size": 1024,
    "distance": "Cosine",
    "hnsw_config": {
        "m": 16,
        "ef_construct": 128,
        "full_scan_threshold": 10000
    },
    "optimizers_config": {
        "deleted_threshold": 0.2,
        "vacuum_min_vector_number": 1000,
        "default_segment_number": 2
    }
}
```

**有效载荷 (Payload):**

```json
{
  "document_id": "uuid-string",
  "content_chunk": "文本块内容",
  "chunk_index": 0,
  "page": 1,
  "section": "第二章",
  "metadata": {
    "title": "文档标题",
    "authors": ["作者1", "作者2"],
    "keywords": ["关键词1", "关键词2"]
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 3.2 分类向量集合

```python
# collection: categories
# 向量维度: 1024
# 距离度量: Cosine

collection_config = {
    "name": "categories",
    "vector_size": 1024,
    "distance": "Cosine"
}
```

**有效载荷 (Payload):**

```json
{
  "category_id": "uuid-string",
  "name": "机器学习",
  "path": "/计算机/AI/机器学习",
  "keywords": ["机器学习", "ML", "深度学习"],
  "description": "关于机器学习的文档",
  "document_count": 156
}
```

---

## 4. 数据库初始化脚本

### 4.1 初始化脚本

```python
#!/usr/bin/env python3
"""
SkyOne Shuge 数据库初始化脚本
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("~/.config/skyone-shuge/data/skyone.db").expanduser()

def init_database():
    """初始化数据库"""
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # 启用外键约束
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 创建表...
    # (上面的 SQL 语句)
    
    # 插入默认分类
    default_categories = [
        ('system', '未分类', None, '/未分类', 'pending', '#9E9E9E'),
        ('system', '计算机科学', None, '/计算机科学', 'system', '#2196F3'),
        ('system', '人工智能', '/计算机科学', '/计算机科学/人工智能', 'system', '#4CAF50'),
    ]
    
    # 提交并关闭
    conn.commit()
    conn.close()
    
    print(f"✓ 数据库已初始化: {DB_PATH}")

if __name__ == "__main__":
    init_database()
```

---

## 5. 数据访问层 (DAL)

### 5.1 Document DAL

```python
from sqlalchemy import create_engine, Column, String, Text, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import List, Optional

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(String(36), primary_key=True)
    file_path = Column(String(1024), nullable=False)
    file_name = Column(String(512), nullable=False)
    file_hash = Column(String(64), unique=True, nullable=False)
    # ... 其他字段
    
    category = relationship("Category", back_populates="documents")
    tags = relationship("Tag", secondary="document_tags")
    
class DocumentDAL:
    """文档数据访问层"""
    
    def __init__(self, session):
        self.session = session
        
    async def create(self, document: Document) -> str:
        """创建文档"""
        self.session.add(document)
        self.session.commit()
        return document.id
    
    async def get_by_id(self, doc_id: str) -> Optional[Document]:
        """根据 ID 获取文档"""
        return self.session.query(Document).filter(
            Document.id == doc_id,
            Document.deleted_at.is_(None)
        ).first()
    
    async def search(
        self,
        query: str = None,
        category_id: str = None,
        tags: List[str] = None,
        status: str = None,
        page: int = 1,
        limit: int = 20
    ):
        """搜索文档"""
        q = self.session.query(Document).filter(
            Document.deleted_at.is_(None)
        )
        
        if query:
            # 全文搜索
            pass
        
        if category_id:
            q = q.filter(Document.category_id == category_id)
            
        if status:
            q = q.filter(Document.status == status)
        
        total = q.count()
        items = q.offset((page - 1) * limit).limit(limit).all()
        
        return {"total": total, "page": page, "items": items}
    
    async def update(self, doc_id: str, **kwargs) -> bool:
        """更新文档"""
        result = self.session.query(Document).filter(
            Document.id == doc_id
        ).update(kwargs)
        
        self.session.commit()
        return result > 0
```

---

## 6. 数据库迁移 (Alembic)

### 6.1 alembic.ini

```ini
[alembic]
script_location = alembic
sqlalchemy.url = sqlite:///./data/skyone.db
```

### 6.2 env.py

```python
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy import engine_from_config
from alembic import context

# 导入模型
from skyone_shuge.models import Base
target_metadata = Base.metadata

def run_migrations():
    connectable = engine_from_config(
        {"sqlalchemy.url": "sqlite:///./data/skyone.db"},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        
        with context.begin_transaction():
            context.run_migrations()
```

---

**版本**: v0.5
**日期**: 2026-02-03
**主题**: 数据库详细设计
