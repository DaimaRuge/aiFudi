# 天一阁 PRD v3.0.6

**版本**: v3.0.6  
**日期**: 2026-03-16  
**阶段**: MVP + API 服务层完善

---

## 📋 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v3.0.6 | 2026-03-16 | API 服务层完整实现：10 个路由模块 + 扩展 Schemas |
| v3.0.5 | 2026-03-10 | RAG 引擎与高级搜索实现（混合搜索、重排序） |
| v3.0.4 | 2026-03-08 | 规划向量存储接口与数据流 |
| v3.0.3 | 2026-03-07 | 实现进展更新：Agent 框架、文档解析器、工作流引擎等 |
| v3.0.2 | 2026-02-25 | 简化 MVP，聚焦 SRT + 知识库，添加 MCP 集成计划 |

---

## 📅 迭代记录 (v3.0.6)

### 本次迭代完成目标
- ✅ **API 层完整实现**：构建基于 FastAPI 的 RESTful 接口，新增 6 个路由模块
- ✅ **路由扩展**：`rag.py`, `tasks.py`, `analytics.py`, `models.py`, `advanced_search.py`, `batch.py`
- ✅ **Schema 扩展**：新增 `rag.py`, `tasks.py`, `analytics.py`, `ml.py` 数据模型
- ✅ **配置增强**：`core/config.py` 扩展任务队列、分析统计等相关配置
- ✅ **API 注册**：`main.py` 和 `routers/__init__.py` 完整注册所有 10 个路由模块

---

## 🎯 一、API 服务层架构

### 1.1 完整路由模块清单 (10 个)

| 路由模块 | 功能 | 端点前缀 |
|---------|------|---------|
| `health` | 健康检查 | `/health` |
| `auth` | 用户认证 (JWT) | `/auth` |
| `documents` | 文档 CRUD | `/documents` |
| `categories` | 分类管理 | `/categories` |
| `search` | 基础搜索 | `/search` |
| `advanced_search` | 高级搜索 (混合/向量) | `/search/advanced` |
| `batch` | 批量操作 | `/batch` |
| `rag` | RAG 问答 | `/rag` |
| `tasks` | 异步任务管理 | `/tasks` |
| `analytics` | 数据分析统计 | `/analytics` |
| `models` | ML 模型管理 | `/models` |

### 1.2 RAG API 端点

**`POST /api/v1/rag/query`**
- 功能：RAG 问答查询
- 请求体：`RAGQueryRequest` (query, top_k, similarity_threshold, stream)
- 响应：`RAGResponse` (answer, sources, confidence)

**`POST /api/v1/rag/feedback`**
- 功能：提交问答反馈
- 请求体：`RAGFeedbackRequest` (query_id, helpful, comment)

**`GET /api/v1/rag/documents/{id}/chunks`**
- 功能：获取文档切分块列表
- 响应：`DocumentChunksResponse`

### 1.3 任务管理 API 端点

**`POST /api/v1/tasks`**
- 功能：创建异步任务
- 支持任务类型：文档索引、重新索引、批量索引、分类同步、Embedding 更新

**`GET /api/v1/tasks/{task_id}`**
- 功能：查询任务状态和进度

**`GET /api/v1/tasks`**
- 功能：任务列表查询
- 支持分页和状态过滤

### 1.4 数据分析 API 端点

**`GET /api/v1/analytics/overview`**
- 功能：数据分析概览
- 指标：日活统计、分类统计、文件类型分布、搜索统计、RAG 统计、存储统计

**`GET /api/v1/analytics/trends`**
- 功能：趋势分析
- 时间范围：day/week/month/quarter/year

---

## 🏗️ 二、数据结构扩展 (Schemas)

### 2.1 RAG 数据模型 (`schemas/rag.py`)

```python
class RAGQueryRequest(BaseModel):
    query: str                    # 用户查询
    top_k: int = 5               # 返回结果数
    similarity_threshold: float  # 相似度阈值
    include_raw_chunks: bool     # 是否包含原始块
    stream: bool                 # 是否流式输出

class RAGSourceDocument(BaseModel):
    document_id: str
    title: Optional[str]
    file_name: str
    chunk_id: str
    chunk_index: int
    content: str
    similarity_score: float

class RAGAnswer(BaseModel):
    answer: str
    sources: List[RAGSourceDocument]
    total_sources: int
    took: float                  # 响应耗时
    generated_at: datetime
```

### 2.2 任务数据模型 (`schemas/tasks.py`)

```python
class TaskStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(str, Enum):
    DOCUMENT_INDEX = "document_index"
    DOCUMENT_REINDEX = "document_reindex"
    BATCH_INDEX = "batch_index"
    EMBEDDING_UPDATE = "embedding_update"

class TaskResponse(BaseModel):
    task_id: str
    task_type: TaskType
    status: TaskStatus
    progress: int              # 0-100
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    result: Optional[Dict]
```

### 2.3 分析统计数据模型 (`schemas/analytics.py`)

```python
class TimeRange(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class DailyStats(BaseModel):
    date: date
    documents_added: int
    documents_indexed: int
    searches: int
    rag_queries: int
    api_requests: int
    storage_used_bytes: int

class AnalyticsOverviewResponse(BaseModel):
    period_start: date
    period_end: date
    daily_stats: List[DailyStats]
    category_stats: List[CategoryStats]
    file_type_stats: List[FileTypeStats]
    search_stats: SearchStats
    rag_stats: RAGStats
    storage_stats: StorageStats
```

---

## 🔌 三、下一步开发计划 (v3.0.7)

### v3.0.7 待办事项
- [ ] **异步任务队列**：引入 Celery/RQ + Redis 实现真正的异步后台任务运行逻辑，对接 TaskRegistry
- [ ] **文档流程整合**：整合文档上传、解析流程，对接 Agent 工作流进行文档端到端处理
- [ ] **前后端联调**：打通端到端的交互链路，完成基础功能闭环
- [ ] **知识图谱扩展**：实体关系抽取与存储基础结构对接

---

**文档结束**  
*下一版本：v3.0.7 (异步任务队列与工作流集成)*
