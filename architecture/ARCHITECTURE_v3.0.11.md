# 天一阁架构文档 v3.0.11

**版本**: v3.0.11
**日期**: 2026-03-28
**主题**: 用户认证界面 + 向量搜索集成 + 高级搜索 + 批量操作 + 导入导出

---

## 📋 版本历史

| 版本 | 日期 | 主题 |
|------|------|------|
| v3.0.11 | 2026-03-28 | 用户认证界面 + 向量搜索集成 + 高级搜索 + 批量操作 + 导入导出 |
| v3.0.10 | 2026-03-25 | WebSocket 前端实现 + Knowledge QA Agent 实现 + 断点续传实现 |

---

## 🏗️ 系统架构概览

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              前端层 (React/TypeScript)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         认证模块                                    │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │ Login Page   │  │ Register     │  │ AuthGuard    │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │                    Auth Store (Zustand)                      │  │   │
│  │  └──────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         搜索模块                                    │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │ Semantic     │  │ Advanced     │  │ Search       │              │   │
│  │  │ Search       │  │ Filters      │  │ Results      │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ WS / HTTP
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            API 层 (FastAPI)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  /auth/login     │  /search/vector   │  /batch/delete              │   │
│  │  /auth/register  │  /search/advanced │  /batch/move                │   │
│  │  /auth/refresh   │  /documents/import│  /batch/tags                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔐 认证架构

### JWT Token 流程

```
登录请求 ──▶ 验证用户 ──▶ 生成 Token 对
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
        Access Token                    Refresh Token
        (30分钟)                        (7天)
              │                               │
              ▼                               ▼
        API 请求携带                   Token 刷新使用
```

### Token 刷新机制

```typescript
// Token 自动刷新
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      await useAuthStore.getState().refreshAccessToken();
      return apiClient(error.config);
    }
    return Promise.reject(error);
  }
);
```

---

## 🔍 向量搜索架构

### 混合搜索 (RRF 融合)

```python
def hybrid_search(query, vector_weight=0.7, keyword_weight=0.3):
    # 向量搜索
    vector_results = vector_search(query, top_k=20)
    
    # 关键词搜索  
    keyword_results = keyword_search(query, top_k=20)
    
    # RRF 融合
    k = 60
    scores = {}
    
    for rank, r in enumerate(vector_results):
        scores[r.id] = scores.get(r.id, 0) + vector_weight * (1 / (k + rank))
    
    for rank, r in enumerate(keyword_results):
        scores[r.id] = scores.get(r.id, 0) + keyword_weight * (1 / (k + rank))
    
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
```

### 语义缓存

```
查询 ──▶ 缓存检查 ──┬──▶ 命中 ──▶ 返回缓存结果
                    │
                    └──▶ 未命中 ──▶ 执行搜索 ──▶ 存储缓存 ──▶ 返回结果
```

---

## 🎯 高级搜索架构

### 过滤器链

```python
class FilterChain:
    def __init__(self):
        self.filters = [
            DocumentTypeFilter(),
            DateRangeFilter(),
            TagFilter(),
            FolderFilter(),
            SizeFilter()
        ]
    
    def apply(self, documents, criteria):
        result = documents
        for f in self.filters:
            if f.should_apply(criteria):
                result = f.apply(result, criteria)
        return result
```

### 排序策略

| 排序方式 | 实现 | 说明 |
|----------|------|------|
| 相关度 | vector_score | 默认降序 |
| 创建时间 | created_at | 可选升降序 |
| 更新时间 | updated_at | 可选升降序 |
| 标题 | title | 字典序 |
| 文件大小 | size | 数值排序 |

---

## 📦 批量操作架构

### 批量操作状态机

```
IDLE ──▶ SELECTING ──┬──▶ MOVING ──┬──▶ SUCCESS
                     │              │
                     ├──▶ TAGGING ──┤
                     │              │
                     └──▶ DELETING ─┘
```

### 批量处理优化

```python
BATCH_SIZE = 100

async def batch_execute(operation, items):
    results = []
    for i in range(0, len(items), BATCH_SIZE):
        batch = items[i:i + BATCH_SIZE]
        batch_results = await asyncio.gather(*[
            operation(item) for item in batch
        ])
        results.extend(batch_results)
    return results
```

---

## 📤📥 导入导出架构

### 导入流程

```
文件上传 ──▶ 格式验证 ──▶ 保存临时文件 ──▶ 创建文档记录
                                              │
                                              ▼
                                         投递 Celery 任务
                                              │
                                              ▼
              进度推送 ◀── WebSocket ◀── 异步处理 (解析/切分/向量化/索引)
```

### 导出格式支持

| 格式 | 元数据 | 内容 | 嵌入向量 | 压缩 |
|------|--------|------|----------|------|
| JSON | ✅ | ✅ | ✅ | ❌ |
| CSV | ✅ | ✅ | ❌ | ❌ |
| TXT | ❌ | ✅ | ❌ | ❌ |
| ZIP | ✅ | ✅ | ❌ | ✅ |

---

## 📁 文件清单

```
skyone-shuge/
├── prd/
│   └── MVP_v3.0.11.md
├── architecture/
│   └── ARCHITECTURE_v3.0.11.md  # 本文档
├── src/frontend/src/
│   ├── pages/
│   │   ├── Login.tsx
│   │   └── Register.tsx
│   ├── components/
│   │   ├── AuthGuard.tsx
│   │   ├── SemanticSearch.tsx
│   │   ├── AdvancedSearchFilters.tsx
│   │   ├── BatchOperationToolbar.tsx
│   │   ├── DocumentImporter.tsx
│   │   └── DocumentExporter.tsx
│   ├── stores/
│   │   ├── authStore.ts
│   │   └── searchStore.ts
│   └── hooks/
│       └── useBatchSelection.ts
└── src/skyone_shuge/
    ├── api/routers/
    │   ├── auth.py
    │   ├── search.py
    │   └── batch.py
    └── services/
        ├── search_service.py
        ├── batch_service.py
        ├── import_service.py
        └── export_service.py
```

---

## 🎯 验收标准

| 模块 | 验收标准 | 状态 |
|------|----------|------|
| 认证 | JWT + 自动刷新 + 路由守卫 | ✅ |
| 向量搜索 | 语义/混合 + 缓存 + 高亮 | ✅ |
| 高级搜索 | 5种过滤 + 5种排序 | ✅ |
| 批量操作 | 选择/移动/标签/删除/导出 | ✅ |
| 导入导出 | 5种格式 + ZIP压缩 | ✅ |

---

## 🚀 下一步 (v3.0.12)

- [ ] LibIndex One 同步服务
- [ ] 项目级管理
- [ ] 协作功能
- [ ] 插件系统
