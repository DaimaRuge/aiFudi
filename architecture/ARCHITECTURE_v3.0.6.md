# 天一阁 架构设计文档 v3.0.6

**版本**: v3.0.6  
**日期**: 2026-03-16  
**架构状态**: API 服务层完整实现

---

## 1. 架构变更记录

| 版本 | 日期 | 核心变更 |
|------|------|----------|
| v3.0.6 | 2026-03-16 | 完整 API 服务层：10 个路由模块 + 扩展 Schemas |
| v3.0.5 | 2026-03-10 | 新增 `RAGEngine` 与 `SearchService`。混合搜索、二次重排集成 |
| v3.0.1 | 2026-03-04 | 统一 Schema 模型、Agent 架构升级 |

---

## 2. API 服务层架构

### 2.1 FastAPI 应用主入口

**位置**: `src/skyone_shuge/api/main.py`

**核心配置**:
```python
app = FastAPI(
    title=settings.APP_NAME,
    description="天一阁 - 智能个人数字文献管理平台",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)
```

**注册路由 (11 个)**:
- `/health` - 健康检查
- `/documents` - 文档管理
- `/categories` - 分类管理
- `/search` - 基础搜索
- `/search/advanced` - 高级搜索
- `/auth` - 用户认证
- `/batch` - 批量操作
- `/rag` - RAG 问答
- `/tasks` - 异步任务
- `/analytics` - 数据分析
- `/models` - ML 模型管理

### 2.2 路由模块详情

#### RAG 路由 (`routers/rag.py`)

**端点**:
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/rag/query` | RAG 问答查询 |
| POST | `/rag/feedback` | 提交问答反馈 |
| GET | `/rag/documents/{id}/chunks` | 获取文档切分块 |

**依赖**:
- `RAGEngine` - 检索增强生成引擎
- `get_async_db` - 异步数据库会话

#### 任务管理路由 (`routers/tasks.py`)

**端点**:
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/tasks` | 创建异步任务 |
| GET | `/tasks/{task_id}` | 查询任务状态 |
| GET | `/tasks` | 任务列表查询 |
| DELETE | `/tasks/{task_id}` | 取消任务 |

**任务类型**:
- `DOCUMENT_INDEX` - 文档索引
- `DOCUMENT_REINDEX` - 文档重新索引
- `DOCUMENT_DELETE` - 文档删除
- `BATCH_INDEX` - 批量索引
- `CATEGORY_SYNC` - 分类同步
- `EMBEDDING_UPDATE` - Embedding 更新
- `ANALYTICS_AGGREGATE` - 分析统计聚合

#### 数据分析路由 (`routers/analytics.py`)

**端点**:
| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/analytics/overview` | 数据分析概览 |
| GET | `/analytics/trends` | 趋势分析 |
| GET | `/analytics/search` | 搜索统计 |
| GET | `/analytics/rag` | RAG 使用统计 |
| GET | `/analytics/storage` | 存储统计 |

**统计维度**:
- 每日统计 (文档添加、索引、搜索、RAG 查询、API 请求、存储使用)
- 分类统计 (文档数、大小、更新时间)
- 文件类型统计 (扩展名、占比)
- 搜索统计 (总搜索数、唯一查询、热门查询)
- RAG 统计 (总查询数、平均来源数、好评率)

#### ML 模型路由 (`routers/models.py`)

**端点**:
| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/models` | 列出可用模型 |
| GET | `/models/{model_id}` | 模型详情 |
| POST | `/models/{model_id}/load` | 加载模型 |
| POST | `/models/{model_id}/unload` | 卸载模型 |
| GET | `/models/status` | 模型状态 |

---

## 3. 扩展数据模型 (Schemas)

### 3.1 RAG Schemas (`schemas/rag.py`)

**请求/响应流**:
```
RAGQueryRequest 
    → RAGEngine.query()
    → RAGAnswer (sources, answer, took)
    → RAGResponse
```

**核心模型**:
- `RAGQueryRequest` - 查询请求
- `RAGSourceDocument` - 源文档信息
- `RAGAnswer` - 生成的回答
- `RAGResponse` - 统一响应包装
- `RAGFeedbackRequest` - 用户反馈
- `ChunkInfo` / `DocumentChunksResponse` - 文档块信息

### 3.2 任务 Schemas (`schemas/tasks.py`)

**状态机**:
```
PENDING → QUEUED → RUNNING → COMPLETED
                    ↓
                  FAILED / CANCELLED
```

**核心模型**:
- `TaskStatus` (Enum) - 任务状态枚举
- `TaskType` (Enum) - 任务类型枚举
- `TaskCreateRequest` - 创建任务请求
- `TaskResponse` - 任务详情响应
- `TaskListResponse` - 任务列表响应
- `TaskStatsResponse` - 任务统计

### 3.3 分析统计 Schemas (`schemas/analytics.py`)

**时间范围**:
- `TimeRange` (Enum): day, week, month, quarter, year

**指标类型**:
- `AnalyticsMetric` (Enum): documents_added, searches, rag_queries, etc.

**核心模型**:
- `DailyStats` - 每日统计
- `CategoryStats` - 分类统计
- `FileTypeStats` - 文件类型统计
- `SearchStats` - 搜索统计
- `RAGStats` - RAG 统计
- `StorageStats` - 存储统计
- `AnalyticsOverviewResponse` - 概览响应
- `AnalyticsRequest` - 分析请求

---

## 4. 配置扩展

### 4.1 新增配置项 (`core/config.py`)

```python
# 任务队列配置
TASK_QUEUE_BACKEND: str = "redis"  # redis / memory
TASK_QUEUE_URL: str = "redis://localhost:6379/0"
TASK_RESULT_EXPIRY: int = 86400   # 24小时

# 分析统计配置
ANALYTICS_RETENTION_DAYS: int = 365
ANALYTICS_AGGREGATION_INTERVAL: int = 3600  # 1小时

# RAG 配置
RAG_DEFAULT_TOP_K: int = 5
RAG_SIMILARITY_THRESHOLD: float = 0.7
RAG_MAX_TOKENS: int = 2048
```

---

## 5. 下一步架构演进

### v3.0.7 规划

- **异步任务队列 (Celery/RQ + Redis)**
  - 将长文档切分、向量化、重排等耗时任务进行异步解耦
  - 对接 `TaskRegistry` 实现任务状态跟踪

- **Agent 工作流接入**
  - 使用现有的 `AgentRegistry`，将检索增强作为 Agent Tool 对外部开放
  - 整合文档上传、解析流程，对接 Agent 工作流进行文档端到端处理

- **前后端联调**
  - 打通端到端的交互链路
  - 完成基础功能闭环

**文档结束**
