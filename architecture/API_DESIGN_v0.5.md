# SkyOne Shuge API 详细设计 v0.5

## 1. API 概览

### 1.1 基本信息

| 项目 | 值 |
|-----|-----|
| 版本 | v1.0 |
| 基础路径 | /api/v1 |
| 认证 | Bearer Token |
| 格式 | JSON |

### 1.2 响应格式

```json
// 成功响应
{
  "success": true,
  "data": {...},
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}

// 错误响应
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "参数验证失败",
    "details": [...]
  }
}
```

---

## 2. 文档管理 API

### 2.1 扫描文档

```yaml
POST /api/v1/documents/scan
Summary: 扫描指定目录

Request:
  Content-Type: application/json
  {
    "paths": ["/path/to/scan"],
    "recursive": true,
    "include_patterns": ["*.pdf", "*.docx"],
    "exclude_patterns": ["*.tmp", "node_modules"],
    "extract_metadata": true,
    "auto_classify": false
  }

Response:
  202 Accepted
  {
    "task_id": "uuid-string",
    "status": "pending",
    "message": "扫描任务已创建"
  }
```

### 2.2 获取文档列表

```yaml
GET /api/v1/documents
Summary: 获取文档列表

Parameters:
  - name: page
    in: query
    type: integer
    default: 1
  - name: limit
    in: query
    type: integer
    default: 20
  - name: category_id
    in: query
    type: string
  - name: status
    in: query
    type: string
    enum: [pending, classified, archived]
  - name: tags
    in: query
    type: array
    items: string
  - name: search
    in: query
    type: string
  - name: sort
    in: query
    type: string
    default: "-updated_at"

Response:
  200 OK
  {
    "success": true,
    "data": [
      {
        "id": "uuid",
        "title": "深度学习入门指南",
        "file_name": "深度学习入门指南.pdf",
        "file_type": "application/pdf",
        "category_id": "uuid",
        "category_path": "/计算机科学/AI/机器学习",
        "tags": ["AI", "Python"],
        "status": "classified",
        "rating": 4,
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "meta": {
      "page": 1,
      "limit": 20,
      "total": 156
    }
  }
```

### 2.3 获取文档详情

```yaml
GET /api/v1/documents/{id}
Summary: 获取文档详情

Response:
  200 OK
  {
    "success": true,
    "data": {
      "id": "uuid",
      "file_path": "/Users/xxx/Documents/book.pdf",
      "file_name": "book.pdf",
      "file_size": 12345678,
      "file_type": "application/pdf",
      "extension": ".pdf",
      
      "title": "深度学习入门指南",
      "subtitle": "第二版",
      "authors": ["吴恩达", "李沐"],
      "publisher": "电子工业出版社",
      "published_date": "2023-01-15",
      "isbn": "978-7-121-12345-6",
      "doi": "10.1234/example",
      
      "abstract": "这是一本深度学习入门书籍...",
      "keywords": ["深度学习", "机器学习", "神经网络"],
      "language": "zh",
      
      "category_id": "uuid",
      "category_path": "/计算机科学/AI/机器学习",
      
      "tags": ["AI", "Python", "机器学习"],
      "status": "classified",
      "rating": 5,
      
      "custom_name": "DL-入门-2023",
      "custom编号": "C001-2024-001",
      
      "indexed_at": "2024-01-15T10:30:00Z",
      "full_text_indexed": true,
      
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  }
```

### 2.4 更新文档

```yaml
PUT /api/v1/documents/{id}
Summary: 更新文档信息

Request:
  {
    "title": "新标题",
    "tags": ["新标签"],
    "category_id": "new-category-uuid",
    "custom_name": "自定义名称",
    "rating": 5
  }

Response:
  200 OK
  {
    "success": true,
    "message": "文档更新成功"
  }
```

### 2.5 删除文档

```yaml
DELETE /api/v1/documents/{id}
Summary: 删除文档 (软删除)

Response:
  200 OK
  {
    "success": true,
    "message": "文档已删除"
  }
```

### 2.6 批量操作

```yaml
POST /api/v1/documents/batch
Summary: 批量操作文档

Request:
  {
    "operation": "move" | "rename" | "tag" | "classify" | "delete",
    "document_ids": ["uuid-1", "uuid-2"],
    "params": {
      "target_category_id": "uuid",
      "tags": ["tag1"],
      "custom_name_prefix": "AI_"
    }
  }

Response:
  200 OK
  {
    "success": true,
    "data": {
      "succeeded": 10,
      "failed": 0,
      "errors": []
    }
  }
```

---

## 3. 分类管理 API

### 3.1 获取分类树

```yaml
GET /api/v1/categories
Summary: 获取分类树

Parameters:
  - name: type
    in: query
    type: string
    enum: [system, user, project]

Response:
  200 OK
  {
    "success": true,
    "data": [
      {
        "id": "uuid",
        "name": "计算机科学",
        "path": "/计算机科学",
        "type": "system",
        "color": "#2196F3",
        "icon": "computer",
        "children": [
          {
            "id": "uuid",
            "name": "人工智能",
            "path": "/计算机科学/人工智能",
            "type": "system",
            "document_count": 156
          }
        ]
      }
    ]
  }
```

### 3.2 创建分类

```yaml
POST /api/v1/categories
Summary: 创建新分类

Request:
  {
    "name": "机器学习",
    "parent_id": "parent-uuid",
    "type": "user",
    "color": "#4CAF50",
    "rules": {
      "keywords": ["ML", "machine learning"],
      "auto_apply": true
    }
  }

Response:
  201 Created
  {
    "success": true,
    "data": {
      "id": "new-uuid",
      "path": "/计算机科学/人工智能/机器学习"
    }
  }
```

### 3.3 更新分类

```yaml
PUT /api/v1/categories/{id}
Summary: 更新分类

Request:
  {
    "name": "深度学习",
    "color": "#FF5722",
    "sort_order": 10
  }

Response:
  200 OK
  {
    "success": true,
    "message": "分类更新成功"
  }
```

### 3.4 删除分类

```yaml
DELETE /api/v1/categories/{id}
Summary: 删除分类

Response:
  200 OK
  {
    "success": true,
    "message": "分类删除成功"
  }
```

---

## 4. AI 功能 API

### 4.1 AI 分类

```yaml
POST /api/v1/ai/classify
Summary: AI 自动分类

Request:
  {
    "document_ids": ["uuid-1", "uuid-2"],
    "strategy": "semantic" | "keyword" | "hybrid",
    "force": false
  }

Response:
  200 OK
  {
    "success": true,
    "data": [
      {
        "document_id": "uuid-1",
        "suggestions": [
          {
            "category_id": "uuid",
            "category_path": "/计算机科学/AI/机器学习",
            "confidence": 0.95
          }
        ],
        "applied": true
      }
    ]
  }
```

### 4.2 AI 提取元数据

```yaml
POST /api/v1/ai/metadata
Summary: AI 提取/补全元数据

Request:
  {
    "document_id": "uuid",
    "fields": ["title", "authors", "abstract", "keywords"]
  }

Response:
  200 OK
  {
    "success": true,
    "data": {
      "title": "深度学习入门指南",
      "authors": ["吴恩达"],
      "abstract": "这是一本...",
      "confidence": 0.92
    }
  }
```

### 4.3 语义搜索

```yaml
POST /api/v1/ai/search
Summary: 语义搜索

Request:
  {
    "query": "什么是卷积神经网络",
    "limit": 10,
    "filters": {
      "category_id": "uuid",
      "tags": ["AI"],
      "date_range": {
        "from": "2023-01-01",
        "to": "2024-01-01"
      }
    },
    "hybrid": true
  }

Response:
  200 OK
  {
    "success": true,
    "data": [
      {
        "document_id": "uuid",
        "title": "卷积神经网络详解",
        "score": 0.95,
        "highlights": ["卷积神经网络是一种..."],
        "category_path": "/计算机科学/AI/深度学习"
      }
    ],
    "meta": {
      "query": "什么是卷积神经网络",
      "vector_search_time": 0.05,
      "total_time": 0.12
    }
  }
```

### 4.4 AI 内容生成

```yaml
POST /api/v1/ai/generate
Summary: AI 内容生成

Request:
  {
    "task": "summary" | "quiz" | "outline" | "presentation" | "mindmap",
    "document_ids": ["uuid-1", "uuid-2"],
    "params": {
      "language": "zh",
      "length": "detailed" | "brief",
      "format": "markdown" | "html"
    }
  }

Response:
  200 OK
  {
    "success": true,
    "data": {
      "content": "# 内容摘要\n\n这是生成的摘要...",
      "format": "markdown"
    }
  }
```

---

## 5. 同步 API

### 5.1 获取同步状态

```yaml
GET /api/v1/sync/status
Summary: 获取同步状态

Response:
  200 OK
  {
    "success": true,
    "data": {
      "enabled": true,
      "last_sync": "2024-01-15T10:00:00Z",
      "pending_uploads": 5,
      "pending_downloads": 2,
      "conflicts": 0,
      "devices": [
        {
          "id": "device-uuid",
          "name": "MacBook Pro",
          "last_seen": "2024-01-15T10:30:00Z"
        }
      ]
    }
  }
```

### 5.2 推送变更

```yaml
POST /api/v1/sync/push
Summary: 推送本地变更

Response:
  200 OK
  {
    "success": true,
    "data": {
      "synced": 10,
      "failed": 0
    }
  }
```

### 5.3 拉取变更

```yaml
POST /api/v1/sync/pull
Summary: 拉取云端变更

Response:
  200 OK
  {
    "success": true,
    "data": {
      "synced": 5,
      "conflicts": [
        {
          "record_id": "uuid",
          "local_version": 10,
          "remote_version": 12
        }
      ]
    }
  }
```

### 5.4 解决冲突

```yaml
POST /api/v1/sync/resolve
Summary: 解决同步冲突

Request:
  {
    "resolutions": [
      {
        "record_id": "uuid",
        "resolution": "keep_local" | "keep_remote" | "merge"
      }
    ]
  }

Response:
  200 OK
  {
    "success": true,
    "message": "冲突已解决"
  }
```

---

## 6. 项目管理 API

### 6.1 获取项目列表

```yaml
GET /api/v1/projects
Summary: 获取项目列表

Response:
  200 OK
  {
    "success": true,
    "data": [
      {
        "id": "uuid",
        "name": "2024 研究项目",
        "description": "深度学习研究",
        "status": "active",
        "document_count": 45,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ]
  }
```

### 6.2 创建项目

```yaml
POST /api/v1/projects
Summary: 创建项目

Request:
  {
    "name": "新项目",
    "description": "项目描述",
    "start_date": "2024-02-01",
    "end_date": "2024-12-31",
    "settings": {
      "default_category": "uuid"
    }
  }

Response:
  201 Created
  {
    "success": true,
    "data": {
      "id": "new-uuid"
    }
  }
```

### 6.3 获取项目文档

```yaml
GET /api/v1/projects/{id}/documents
Summary: 获取项目文档

Response:
  200 OK
  {
    "success": true,
    "data": [
      {
        "document_id": "uuid",
        "role": "primary",
        "added_at": "2024-01-15T10:00:00Z",
        "document": {
          "title": "研究论文",
          "category_path": "/计算机科学/AI"
        }
      }
    ]
  }
```

---

## 7. 搜索 API

### 7.1 高级搜索

```yaml
GET /api/v1/search
Summary: 高级搜索

Parameters:
  - name: q
    in: query
    type: string
    required: true
  - name: category_id
    in: query
    type: string
  - name: tags
    in: query
    type: array
  - name: file_type
    in: query
    type: array
  - name: date_from
    in: query
    type: string
  - name: date_to
    in: query
    type: string
  - name: page
    in: query
    type: integer
  - name: limit
    in: query
    type: integer
  - name: sort
    in: query
    type: string
  - name: mode
    in: query
    type: string
    enum: [keyword, semantic, hybrid]

Response:
  200 OK
  {
    "success": true,
    "data": [...],
    "meta": {
      "total": 100,
      "page": 1,
      "took": 0.05
    }
  }
```

---

## 8. 错误码定义

| 错误码 | HTTP 状态 | 说明 |
|-------|----------|------|
| VALIDATION_ERROR | 400 | 参数验证失败 |
| UNAUTHORIZED | 401 | 未授权 |
| FORBIDDEN | 403 | 禁止访问 |
| NOT_FOUND | 404 | 资源不存在 |
| CONFLICT | 409 | 资源冲突 |
| UNPROCESSABLE_ENTITY | 422 | 业务逻辑错误 |
| INTERNAL_ERROR | 500 | 服务器错误 |
| SERVICE_UNAVAILABLE | 503 | 服务不可用 |

---

**版本**: v0.5
**日期**: 2026-02-03
**主题**: API 详细设计
