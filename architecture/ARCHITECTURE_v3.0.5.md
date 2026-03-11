# 天一阁 架构设计文档 v3.0.5

**版本**: v3.0.5  
**日期**: 2026-03-10  
**架构状态**: RAG 引擎与高级搜索服务集成

---

## 1. 架构变更记录

| 版本 | 日期 | 核心变更 |
|------|------|----------|
| v3.0.5 | 2026-03-10 | 新增 `RAGEngine` 与 `SearchService`。混合搜索、二次重排集成 |
| v3.0.1 | 2026-03-04 | 统一 Schema 模型、Agent 架构升级 |

---

## 2. 核心服务架构 (Service Layer)

### 2.1 RAGEngine (检索增强生成引擎)
**位置**: `src/skyone_shuge/ml/rag.py`

**主要职责**:
1. **意图分析 (`_analyze_query`)**: 提取关键词，识别用户查询类型和领域需求。
2. **多路检索 (`_retrieve_documents`)**: 基于策略 (混合、向量、关键词) 从向量库和关系库检索相关的文档分块。
3. **二次重排 (`_rerank_documents`)**: 通过规则计算或 Cross-Encoder 提升强相关性块的排名。
4. **答案生成 (`_generate_answer`)**: 将高质量的 Top-K 文档和分析后的上下文组装为 Prompt，请求 LLM 生成结构化答案和推理过程。

**涉及组件**:
- `EmbeddingService`：用于查询向量化。
- `VectorDatabase` (Qdrant)：用于相似度召回。
- `LLMService`：用于意图理解和结果生成。

### 2.2 SearchService (高级搜索服务)
**位置**: `src/skyone_shuge/services/search_service.py`

**主要职责**:
1. **统一查询接口**: 接收 `SearchQuery` 对象，分配检索策略。
2. **向量搜索 (`_vector_search`)**: 调用 RAG 引擎的向量检索功能。
3. **关键词搜索 (`_keyword_search`)**: 调用关系型数据库的全文或模式匹配检索。
4. **混合召回 (`_merge_results`)**: 将向量分数和关键词匹配分数按权重合并。
5. **元数据过滤 (`_apply_filters`)**: 对检索范围 (文件类型、时间范围、分类) 进行精准过滤。

---

## 3. 核心数据对象 (Schemas)

**位置**: `src/skyone_shuge/schemas/search.py`

### 3.1 搜索查询层
```python
class SearchQuery(BaseModel):
    query: str
    search_type: SearchType = SearchType.HYBRID
    filters: Optional[SearchFilter]
    enable_rerank: bool = True
    page: int = 1
    page_size: int = 20
```

### 3.2 搜索过滤层
```python
class SearchFilter(BaseModel):
    document_ids: Optional[List[str]]
    category_ids: Optional[List[int]]
    tags: Optional[List[str]]
    created_after: Optional[datetime]
    created_before: Optional[datetime]
    file_types: Optional[List[str]]
```

### 3.3 检索响应层 (RAG)
```python
class RAGResponse(BaseModel):
    answer: str
    sources: List[RAGSource]
    confidence: float
    reasoning: Optional[str]
```

---

## 4. RAG 与搜索工作流

1. **请求接入**: API 接收 `SearchQuery`，转发至 `SearchService`。
2. **过滤构建**: `SearchService` 提取 `SearchFilter` 中配置的限定范围（如限制只查询某分类的 PDF）。
3. **混合召回**:
   - `SearchService` 将查询语句传给 `EmbeddingService` 向量化，并请求 `VectorDatabase` 返回 Top-K 向量。
   - `SearchService` 针对关系型数据库执行 `LIKE` / 匹配查询。
4. **合并重排**:
   - 如果开启 `enable_rerank`，结果交由 `RAGEngine` 的 `_rerank_documents` 执行二次打分。
5. **知识生成 (针对 RAG)**:
   - 过滤低分块后，`RAGEngine` 组装系统提示词，通过 `LLMService` 生成结构化的 JSON（答案 + 推理）。
6. **组合返回**:
   - 最终返回带有元数据引用、置信度、答案片段的统一对象。

---

## 5. 下一步架构演进
- **API 层级 (`src/skyone_shuge/api/`)**: 将服务接口暴漏为 HTTP 端点（FastAPI）。
- **异步任务队列 (Celery / BackgroundTasks)**: 将长文档切分、向量化、重排等耗时任务进行异步解耦。
- **Agent 工作流接入**: 使用现有的 AgentRegistry，将检索增强作为 Agent Tool 对外部开放。

**文档结束**