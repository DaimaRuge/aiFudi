# 天一阁 - MVP v3.0.6 产品需求文档 (PRD)

## 1. 迭代目标
本次迭代 (v3.0.6) 主要目标是完善 API 层实现（RESTful endpoints）并提供文档上传、异步任务处理队列（Celery/RQ）的数据模型，以及 RAG、ML、搜索分析等高阶功能的路由。使之前已实现的工作流和算法能够通过统一的 HTTP 接口暴露给前端和外部系统调用。

## 2. 核心功能点
### 2.1 API 路由完善
- **RAG问答接口 (`/api/v1/rag`)**: 暴露已实现的 RAGEngine，支持多轮交互和引用溯源。
- **搜索增强接口 (`/api/v1/search` & `/api/v1/advanced_search`)**: 支持元数据过滤、混合搜索和基于大语言模型的重排。
- **机器学习模型状态监控 (`/api/v1/models`)**: 支持随时查询底层大模型（如Ark/OpenAI）和向量模型的健康度、参数配置。
- **批量操作接口 (`/api/v1/batch`)**: 对文档集合进行批量重排序、打标、分类等操作。

### 2.2 异步任务体系（设计层面）
- 设计 `schemas/tasks.py` 用于标准化异步任务的状态机（PENDING, RUNNING, COMPLETED, FAILED）。
- 提供 `/api/v1/tasks` 接口，方便前端对长耗时任务（如长文档切分、全量重新向量化）进行进度查询和管理。

### 2.3 数据分析大盘接口
- 设计 `/api/v1/analytics/overview` 接口提供全维度数据指标：文档索引数、分类统计、存储用量、模型调用次数等，以支持前端构建 Dashboard。

## 3. 技术设计方案
### 3.1 Pydantic Schemas 数据模型设计
统一的入参出参模型放置于 `schemas/` 下，实现：
- `rag.py`: RAGQueryRequest、RAGAnswer、RAGSourceDocument 等。
- `tasks.py`: TaskCreateRequest、TaskResponse 等。
- `ml.py`: EmbeddingModelInfo、LLMCompletionRequest 等。
- `analytics.py`: DailyStats、AnalyticsOverviewResponse 等。

### 3.2 FastAPI 路由挂载
更新 `api/main.py` 的注册中心，使用 `API_V1_PREFIX` 统一管理版本前缀，并成功挂载：
- `rag.router`
- `tasks.router`
- `analytics.router`
- `models.router`
- `advanced_search.router`
- `batch.router`

## 4. 下一步计划
- **v3.0.7**: 引入 Celery 和 Redis 实现真正的异步后台任务运行逻辑，对接 `DocumentProcessor` 和 `TaskRegistry`。
- **v3.1.0**: 前后端联调，打通端到端的交互链路。
