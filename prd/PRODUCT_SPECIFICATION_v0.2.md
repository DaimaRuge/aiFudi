# SkyOne Shuge (天一阁) PRD v0.2
**版本日期**: 2026-02-03
**状态**: 迭代中

---

## 1. 产品概述

### 1.1 产品愿景
天一阁是一个基于大模型的智能个人数字文献管理与认知增强平台，帮助用户建立格式化、有序的个人知识索引体系，并通过 AI 深化认知结构。

### 1.2 核心定位
- **数字图书馆**: 格式化、有序的文献索引
- **认知分析器**: 通过 AI 深化个人知识结构
- **创作工场**: 基于知识体系生成各类内容

### 1.3 目标用户画像

| 用户类型 | 核心需求 | 典型场景 |
|---------|---------|---------|
| 学术研究者 | 系统化管理论文、文献 | 论文写作、文献综述 |
| 知识工作者 | 知识积累与检索 | 项目研究、行业分析 |
| 专业人员 | 法规、案例、技术文档管理 | 执业准备、工作参考 |
| 学生 | 教材、笔记、考试资料管理 | 学习备考、课程作业 |
| 终身学习者 | 跨领域知识体系构建 | 技能提升、兴趣探索 |

---

## 2. 核心功能模块

### 2.1 LibIndex 数字文献索引系统

#### 2.1.1 设备级索引 (LibIndex Device)

**核心能力:**

| 能力 | 描述 | 技术要点 |
|-----|------|---------|
| 多源扫描 | 本地磁盘、外接存储、云网盘 (iCloud/OneDrive/Dropbox) | 增量扫描、变更检测 |
| 格式解析 | 文档、音视频、代码、压缩包等 50+ 格式 | 专用解析库 |
| 元数据提取 | 标题、作者、ISBN、DOI、页数、时长等 | AI + 规则混合 |
| 智能命名 | 按用户/专业规则重命名、编号 | 模板引擎 |
| 实时监控 | 文件增删改自动同步索引 | inotify/FSEvents |

**支持格式清单:**

```
文档类:
├── PDF (.pdf)
├── Word (.docx)
├── Excel (.xlsx)
├── PowerPoint (.pptx)
├── Markdown (.md)
├── Text (.txt)
├── JSON/XML/HTML (.json, .xml, .html)
├── EPUB (.epub)
├── Rich Text (.rtf)
└── OpenDocument (.odt, .ods, .odp)

代码类:
├── Python (.py)
├── JavaScript/TypeScript (.js, .ts)
├── Java/Kotlin (.java, .kt)
├── C/C++ (.c, .cpp, .h, .hpp)
├── Go (.go)
├── Rust (.rs)
├── SQL (.sql)
└── 其他语言

音视频类:
├── 音频: MP3, WAV, FLAC, AAC, M4A, OGG
└── 视频: MP4, MKV, AVI, MOV, WEBM, FLV

归档类:
└── ZIP, RAR, 7z (解压扫描内部文档)
```

#### 2.1.2 云端同步 (LibIndex One)

**架构设计:**

```
┌─────────────┐     HTTPS      ┌──────────────┐
│  Device A   │ ◄──────────►  │  LibIndex    │
│  (本地)      │   索引同步     │  One (云端)   │
└─────────────┘               └──────────────┘
      │                               ▲
      │ HTTPS                         │
      ▼                               │
┌─────────────┐                       │
│  Device B   │ ◄────────────────────┘
│  (本地)      │      索引同步
└─────────────┘
```

**同步模式:**

| 模式 | 描述 | 适用场景 |
|-----|------|---------|
| 单向推送 | 本地 → 云端 | 备份为主 |
| 双向同步 | 本地 ↔ 云端 | 多设备协作 |
| 主从同步 | 指定设备为 Master | 个人工作站 + 移动端 |
| 按需拉取 | 手动触发下载 | 节省带宽 |
| 离线模式 | 不同步，合并时导入 | 物理隔离环境 |

**冲突处理策略:**

1. **时间优先**: 最新修改覆盖旧版本
2. **用户选择**: 冲突时提示用户选择
3. **自动合并**: 同名字段取并集
4. **版本保留**: 保留历史版本

#### 2.1.3 命名与编号规则

**系统预设规则:**

```
中图法格式: {大类}{中类}{小类}/{作者}/{书名}_{年份}
示例: O243/张三/机器学习导论_2023.pdf

用户自定义模板:
{name}_{authors}_{year}_{tags}
{name}_{custom_no}
```

### 2.2 AI 智能分类与元数据增强

#### 2.2.1 分类引擎

**双重分类体系:**

```
┌──────────────────────────────────────────────────────┐
│                    分类引擎                             │
├──────────────────────┬───────────────────────────────┤
│     标准分类          │         个性化分类             │
├──────────────────────┼───────────────────────────────┤
│ • 中图法             │ • 用户自定义文件夹            │
│ • 杜威十进分类法      │ • 项目分类                    │
│ • 学科分类 (理工科...) │ • 场景分类 (工作/学习/娱乐)   │
│ • 行业分类           │ • 状态分类 (待读/在读/已读)   │
└──────────────────────┴───────────────────────────────┘
```

**AI 分类流程:**

```
文档扫描 → 文本提取 → 语义向量 → 相似度匹配 → 候选分类 → 用户确认 → 正式归类
```

#### 2.2.2 元数据补全 Agent

**数据源:**

| 数据源 | 类型 | 用途 |
|-------|------|------|
| 公共图书馆 (LoC, ISBNdb) | 书名、作者、ISBN | 书名补全 |
| 学术数据库 (Semantic Scholar, arXiv) | 论文、引用 | 论文元数据 |
| 电商平台 (Amazon, JD) | 封面、评分 | 推荐相关 |
| 知识图谱 | 主题、关联 | 智能推荐 |

### 2.3 无涯子 (Wuya Study) - 认知引擎

#### 2.3.1 核心功能

| 功能 | 描述 | AI 能力 |
|-----|------|---------|
| 知识问答 | 基于藏书的精准问答 | RAG |
| 概念图谱 | 可视化知识关联 | 知识图谱 |
| 文献综述 | 自动生成研究综述 | 摘要+综合 |
| 内容生成 | 报告、PPT、视频脚本 | 生成式 AI |
| 测试生成 | 习题、试卷生成 | 教育 AI |

#### 2.3.2 认知结构分析

```
藏书分析 → 知识盲区识别 → 学习建议 → 认知路径规划
```

### 2.4 教育体系模块

**学制配置:**

```
┌─────────────────────────────────────────────────────┐
│                    学制配置                           │
├─────────────────────────────────────────────────────┤
│ 中国学制                                              │
│   学前教育 (3-6岁) → 小学 (6-12岁) → 初中 (12-15)   │
│   → 高中 (15-18) → 本科 (18-22) → 研究生 (22+)       │
├─────────────────────────────────────────────────────┤
│ 美国学制                                              │
│   Preschool → K-12 → Undergrad → Graduate            │
└─────────────────────────────────────────────────────┘
```

**专业学习路径:**

```
硬件设计: 电路基础 → PCB设计 → 嵌入式 → FPGA
软件开发: 编程基础 → 框架学习 → 系统架构 → DevOps
法律执业: 法考 → 实务 → 专精领域
医学执业: 基础医学 → 临床 → 专科
```

### 2.5 项目级文献管理

```
项目视图:
├── 项目文档 (合同、技术方案、会议纪要)
├── 参考文献 (论文、报告、标准)
├── 产出物 (代码、演示文稿、报告)
└── 上下文 (项目背景、约束条件)
```

---

## 3. 技术架构

### 3.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        SkyOne Shuge                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Web UI      │  │   Desktop    │  │     CLI              │  │
│  │  (React)      │  │ (Electron)   │  │   (Rust/Python)      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    API Gateway                            │  │
│  │               (FastAPI / Actix-web)                       │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                    业务服务层                                   │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │ 扫描服务   │ │ 索引服务   │ │ 分类服务   │ │ 同步服务   │   │
│  │ Scanner    │ │ Indexer    │ │ Classifier │ │ Syncer     │   │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                    AI 能力层                                    │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │ LLM 路由   │ │ 向量化     │ │ RAG 引擎   │ │ Agent      │   │
│  │ Router    │ │ Embedding  │ │ Retrieval  │ │ Orchestrator│   │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                    数据持久层                                    │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐   │
│  │ SQLite/       │  │  Redis        │  │ 向量数据库      │   │
│  │ PostgreSQL    │  │  (缓存/队列)   │  │ (Qdrant/Milvus)│   │
│  └────────────────┘  └────────────────┘  └─────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                    文件存储                                     │
│  ┌────────────┐  ┌────────────┐  ┌───────────────────────────┐ │
│  │ 本地存储   │  │ 云网盘挂载  │  │ 临时文件管理              │ │
│  └────────────┘  └────────────┘  └───────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 技术选型

| 层级 | 技术 | 选型理由 |
|-----|------|---------|
| **后端** | Python (FastAPI) / Rust (Actix) | 高性能、异步 |
| **前端** | React + TypeScript | 生态丰富、类型安全 |
| **桌面** | Tauri / Electron | 跨平台、Native 体验 |
| **数据库** | SQLite (端侧) + PostgreSQL (云端) | 轻量 + 强大 |
| **向量库** | Qdrant / Milvus | 高效向量检索 |
| **文件处理** | Rust 库集群 | 高性能、内存安全 |
| **LLM 框架** | LangChain / LlamaIndex | 成熟、生态丰富 |
| **OCR** | PaddleOCR / Tesseract | 中文优化 |

### 3.3 大模型集成

**支持的模型:**

```python
LLM_PROVIDERS = {
    "openai": {"models": ["gpt-4", "gpt-4-turbo"], "strength": "通用"},
    "anthropic": {"models": ["claude-3-opus", "claude-3-sonnet"], "strength": "长文本"},
    "google": {"models": ["gemini-pro"], "strength": "多模态"},
    "minimax": {"models": ["minimax-01"], "strength": "中文优化"},
    "baidu": {"models": ["ernie-4.0"], "strength": "中文理解"},
    "alibaba": {"models": ["qwen-turbo", "qwen-plus"], "strength": "代码"},
    "zhipu": {"models": ["glm-4"], "strength": "知识问答"},
}
```

**功能映射:**

| 功能 | 推荐模型 | 成本敏感 |
|-----|---------|---------|
| 文档分类 | GPT-4 / Claude 3 | 高 |
| 元数据提取 | Qwen-Plus / GPT-3.5 | 中 |
| 知识问答 | Claude 3 / GPT-4 | 高 |
| 内容生成 | GPT-4 / Claude 3 | 高 |
| 代码生成 | Claude 3 / Qwen-Plus | 中 |
| 摘要生成 | GPT-3.5 / Claude Haiku | 低 |

---

## 4. 数据库设计 (v0.2)

### 4.1 核心表结构

```sql
-- 文档主表
CREATE TABLE documents (
    id TEXT PRIMARY KEY,                    -- UUID
    file_path TEXT NOT NULL,               -- 原始文件路径
    file_name TEXT NOT NULL,               -- 原始文件名
    file_hash TEXT UNIQUE,                 -- 文件哈希 (去重)
    file_size BIGINT,                      -- 文件大小 (字节)
    file_type TEXT,                        -- 文件 MIME 类型
    extension TEXT,                        -- 扩展名
    
    -- 元数据字段
    title TEXT,
    subtitle TEXT,
    authors TEXT[],                        -- PostgreSQL 数组
    publisher TEXT,
    published_date DATE,
    isbn TEXT,
    doi TEXT,
    volume TEXT,
    issue TEXT,
    pages TEXT,
    abstract TEXT,
    keywords TEXT[],
    language TEXT,
    
    -- 分类与标签
    category_id TEXT,                      -- 分类 ID
    category_path TEXT,                    -- 分类路径 (冗余)
    tags TEXT[],                           -- 用户标签
    status TEXT DEFAULT 'pending',          -- pending/classified/archived
    rating INTEGER,                        -- 1-5 星级
    
    -- 自定义命名
    custom_name TEXT,
    custom编号 TEXT,
    
    -- 索引信息
    indexed_at TIMESTAMP,
    vector_embedding JSONB,                -- 向量嵌入
    full_text_indexed BOOLEAN DEFAULT FALSE,
    
    -- 同步信息
    sync_status TEXT DEFAULT 'synced',
    sync_version INTEGER DEFAULT 0,
    last_synced_at TIMESTAMP,
    device_id TEXT,                        -- 来源设备
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP,
    
    CONSTRAINT fk_category FOREIGN KEY (category_id)
        REFERENCES categories(id) ON DELETE SET NULL
);

-- 分类表
CREATE TABLE categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id TEXT,
    path TEXT NOT NULL,                   -- /学术/计算机/AI
    type TEXT DEFAULT 'user',             -- system/user/project
    description TEXT,
    color TEXT,                           -- UI 显示颜色
    icon TEXT,
    sort_order INTEGER DEFAULT 0,
    rules JSONB,                          -- 自动分类规则
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT fk_parent FOREIGN KEY (parent_id)
        REFERENCES categories(id) ON DELETE CASCADE
);

-- 标签表 (多对多)
CREATE TABLE tags (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    color TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE document_tags (
    document_id TEXT REFERENCES documents(id) ON DELETE CASCADE,
    tag_id TEXT REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (document_id, tag_id)
);

-- 项目表
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',         -- active/archived/completed
    start_date DATE,
    end_date DATE,
    owner_id TEXT,                         -- 所有者
    settings JSONB,                        -- 项目配置
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 项目-文档关联
CREATE TABLE project_documents (
    project_id TEXT REFERENCES projects(id) ON DELETE CASCADE,
    document_id TEXT REFERENCES documents(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'reference',         -- primary/reference/derived
    added_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (project_id, document_id)
);

-- 设备表
CREATE TABLE devices (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT,                             -- desktop/mobile/server
    platform TEXT,                         -- windows/macos/linux
    last_seen_at TIMESTAMP,
    sync_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 同步日志
CREATE TABLE sync_logs (
    id TEXT PRIMARY KEY,
    device_id TEXT NOT NULL,
    operation TEXT,                        -- create/update/delete
    table_name TEXT,
    record_id TEXT,
    payload JSONB,
    timestamp TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'pending',         -- pending/synced/failed
    error_message TEXT
);

-- 用户配置
CREATE TABLE user_configs (
    key TEXT PRIMARY KEY,
    value JSONB,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引 (优化查询)
CREATE INDEX idx_documents_category ON documents(category_id);
CREATE INDEX idx_documents_tags ON documents USING GIN(tags);
CREATE INDEX idx_documents_hash ON documents(file_hash);
CREATE INDEX idx_documents_updated ON documents(updated_at);
CREATE INDEX idx_documents_status ON documents(status);
```

### 4.2 向量数据库设计

```python
# 文档向量集合
Collection: documents
Fields:
    - id: str (文档 ID)
    - document_id: str (外键)
    - content_chunk: str (文本块)
    - embedding: List[float] (1536 维向量)
    - metadata: dict (页码、章节等)
    - created_at: datetime
```

---

## 5. API 接口设计 (v0.2)

### 5.1 API 规范

```yaml
openapi: 3.1.0
info:
  title: SkyOne Shuge API
  version: 1.0.0
  description: 天一阁数字文献管理平台 API

servers:
  - url: http://localhost:8080/api/v1
    description: 本地开发服务器
  - url: https://api.skyoneshuge.com/api/v1
    description: 生产环境

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer

security:
  - BearerAuth: []

tags:
  - name: documents
    description: 文献管理
  - name: categories
    description: 分类管理
  - name: sync
    description: 同步服务
  - name: ai
    description: AI 功能
  - name: projects
    description: 项目管理
  - name: search
    description: 搜索服务
```

### 5.2 接口列表

#### 5.2.1 文献管理

```yaml
paths:
  /documents/scan:
    post:
      tags: [documents]
      summary: 扫描目录
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                paths:
                  type: array
                  items:
                    type: string
                  description: 待扫描路径列表
                recursive:
                  type: boolean
                  default: true
                include_patterns:
                  type: array
                  items:
                    type: string
                  description: 文件名匹配模式
                exclude_patterns:
                  type: array
                  items:
                    type: string
              required: [paths]
      responses:
        '200':
          description: 扫描任务已创建
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ScanTask'

  /documents:
    get:
      tags: [documents]
      summary: 获取文档列表
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
        - name: category_id
          in: query
          schema:
            type: string
        - name: status
          in: query
          schema:
            type: string
            enum: [pending, classified, archived]
        - name: search
          in: query
          schema:
            type: string
        - name: tags
          in: query
          schema:
            type: array
            items:
              type: string
      responses:
        '200':
          description: 文档列表
          content:
            application/json:
              schema:
                type: object
                properties:
                  total:
                    type: integer
                  page:
                    type: integer
                  items:
                    type: array
                    items:
                      $ref: '#/components/schemas/Document'

  /documents/{id}:
    get:
      tags: [documents]
      summary: 获取文档详情
    put:
      tags: [documents]
      summary: 更新文档
    delete:
      tags: [documents]
      summary: 删除文档

  /documents/{id}/metadata:
    get:
      tags: [documents]
      summary: 获取文档元数据
    put:
      tags: [documents]
      summary: 更新文档元数据

  /documents/{id}/classify:
    post:
      tags: [documents]
      summary: AI 重新分类
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                force:
                  type: boolean
                  default: false
                  description: 强制重新分类
      responses:
        '200':
          description: 分类结果
          content:
            application/json:
              schema:
                type: object
                properties:
                  suggestions:
                    type: array
                    items:
                      $ref: '#/components/schemas/CategorySuggestion'
                  confidence:
                    type: number

  /documents/batch:
    post:
      tags: [documents]
      summary: 批量操作
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                operation:
                  type: string
                  enum: [move, rename, tag, classify, delete]
                document_ids:
                  type: array
                  items:
                    type: string
                params:
                  type: object
```

#### 5.2.2 分类管理

```yaml
paths:
  /categories:
    get:
      tags: [categories]
      summary: 获取分类树
      parameters:
        - name: type
          in: query
          schema:
            type: string
            enum: [system, user, project]
    post:
      tags: [categories]
      summary: 创建分类

  /categories/{id}:
    get:
      tags: [categories]
      summary: 获取分类详情
    put:
      tags: [categories]
      summary: 更新分类
    delete:
      tags: [categories]
      summary: 删除分类

  /categories/batch:
    post:
      tags: [categories]
      summary: 批量移动/重命名
```

#### 5.2.3 同步服务

```yaml
paths:
  /sync/status:
    get:
      tags: [sync]
      summary: 获取同步状态

  /sync/push:
    post:
      tags: [sync]
      summary: 推送本地变更

  /sync/pull:
    post:
      tags: [sync]
      summary: 拉取云端变更

  /sync/resolve:
    post:
      tags: [sync]
      summary: 解决同步冲突
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                conflicts:
                  type: array
                  items:
                    type: object
                    properties:
                      record_id:
                        type: string
                      local_version:
                        type: integer
                      remote_version:
                        type: integer
                      resolution:
                        type: string
                        enum: [keep_local, keep_remote, merge]
```

#### 5.2.4 AI 功能

```yaml
paths:
  /ai/classify:
    post:
      tags: [ai]
      summary: AI 文档分类
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                document_ids:
                  type: array
                  items:
                    type: string
                strategy:
                  type: string
                  enum: [semantic, keyword, hybrid]
      responses:
        '200':
          description: 分类结果

  /ai/metadata:
    post:
      tags: [ai]
      summary: AI 提取/补全元数据
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                document_id:
                  type: string
                fields:
                  type: array
                  items:
                    type: string
                    enum: [title, authors, abstract, keywords, doi, isbn]

  /ai/search:
    post:
      tags: [ai, search]
      summary: 语义搜索
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                query:
                  type: string
                limit:
                  type: integer
                  default: 10
                filters:
                  type: object
      responses:
        '200':
          description: 搜索结果

  /ai/generate:
    post:
      tags: [ai]
      summary: AI 内容生成
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                task:
                  type: string
                  enum: [summary, quiz, outline, presentation, mindmap]
                document_ids:
                  type: array
                  items:
                    type: string
                params:
                  type: object
```

#### 5.2.5 项目管理

```yaml
paths:
  /projects:
    get:
      tags: [projects]
      summary: 获取项目列表
    post:
      tags: [projects]
      summary: 创建项目

  /projects/{id}:
    get:
      tags: [projects]
      summary: 获取项目详情
    put:
      tags: [projects]
      summary: 更新项目
    delete:
      tags: [projects]
      summary: 删除项目

  /projects/{id}/documents:
    get:
      tags: [projects]
      summary: 获取项目文档
    post:
      tags: [projects]
      summary: 添加文档到项目
    delete:
      tags: [projects]
      summary: 从项目移除文档

  /projects/{id}/generate:
    post:
      tags: [projects]
      summary: 生成项目报告
```

### 5.3 数据模型 (Schema)

```yaml
components:
  schemas:
    Document:
      type: object
      properties:
        id:
          type: string
        title:
          type: string
        authors:
          type: array
          items:
            type: string
        file_path:
          type: string
        file_type:
          type: string
        category_id:
          type: string
        tags:
          type: array
          items:
            type: string
        status:
          type: string
          enum: [pending, classified, archived]
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    Category:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        parent_id:
          type: string
        path:
          type: string
        type:
          type: string
          enum: [system, user, project]

    ScanTask:
      type: object
      properties:
        task_id:
          type: string
        status:
          type: string
          enum: [pending, scanning, completed, failed]
        total_files:
          type: integer
        scanned_files:
          type: integer
        errors:
          type: array
```

---

## 6. 隐私与安全

### 6.1 数据隐私

| 数据 | 存储位置 | 同步 | 加密 |
|-----|---------|-----|-----|
| 文献原文 | 本地设备 | 可选 | 可选 (用户密钥) |
| 元数据 | 本地 + 云端 | 默认 | TLS |
| 向量索引 | 本地设备 | 不同步 | - |
| 用户配置 | 本地 + 云端 | 默认 | TLS |
| AI 交互日志 | 不存储 | - | - |

### 6.2 安全措施

- **传输加密**: 全站 HTTPS/TLS
- **本地加密**: 用户主密钥加密敏感文件
- **访问控制**: 设备绑定、访问令牌
- **隐私模式**: AI 功能可完全离线运行

### 6.3 用户控制

- 同步开关 (全局/按项目)
- 云端数据一键删除
- 导出/备份控制
- AI 功能权限 (联网/离线)

---

## 7. 性能指标

| 指标 | 目标值 | 测量方式 |
|-----|-------|---------|
| 文档扫描速度 | > 100 文件/秒 | 10K 文档测试 |
| 索引查询延迟 | < 100ms (P95) | 100K 文档 |
| 同步延迟 | < 1 秒 | 增量同步 |
| 搜索延迟 | < 200ms | 语义搜索 |
| 内存占用 | < 500MB (空闲) | 桌面端 |
| 冷启动时间 | < 3 秒 | 桌面端 |

---

## 8. 迭代计划

### v0.1 ✅ 已完成
- [x] 产品概述与愿景
- [x] 核心功能定义
- [x] 技术架构初稿
- [x] 使用场景分析

### v0.2 ✅ 当前版本
- [x] 详细数据库表结构
- [x] API 接口规范
- [x] 分类引擎设计
- [x] 向量数据库设计

### v0.3 待执行
- [ ] MVP 功能优先级
- [ ] 开发任务拆分 (WBS)
- [ ] 技术栈最终确认
- [ ] 项目目录结构
- [ ] 开发规范文档

### v0.4 待执行
- [ ] 详细 UI/UX 原型
- [ ] 用户流程图
- [ ] 交互设计稿

---

## 9. 附录

### 9.1 术语表

| 术语 | 定义 |
|-----|------|
| LibIndex | 数字文献索引数据库 |
| LibIndex Device | 设备本地的索引库 |
| LibIndex One | 云端同步服务 |
| 无涯子 | AI 认知增强模块 |
| 向量索引 | 文档语义向量存储 |

### 9.2 参考资料

- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic Claude](https://docs.anthropic.com)
- [FastAPI](https://fastapi.tiangolo.com)
- [Qdrant Vector Database](https://qdrant.tech/documentation)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)

---

**作者**: AI Assistant
**创建日期**: 2026-02-03
**更新日期**: 2026-02-03
