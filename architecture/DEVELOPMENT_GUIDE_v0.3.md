# SkyOne Shuge 开发规范 v0.3

## 目录

1. [项目结构](#1-项目结构)
2. [代码规范](#2-代码规范)
3. [Git 工作流](#3-git-工作流)
4. [API 设计规范](#4-api-设计规范)
5. [测试规范](#5-测试规范)
6. [部署规范](#6-部署规范)

---

## 1. 项目结构

```
skyone-shuge/
├── .github/workflows/     # CI/CD
├── docs/                  # 文档
├── scripts/               # 脚本
├── skyone_shuge/          # 后端
│   ├── core/            # 配置
│   ├── models/          # 数据模型
│   ├── services/        # 业务逻辑
│   ├── api/             # FastAPI
│   ├── cli/             # CLI
│   └── ml/              # AI/ML
├── frontend/             # 前端 React
└── tests/                # 测试
```

---

## 2. 代码规范

### 2.1 Python

```toml
# pyproject.toml
[tool.black]
line-length = 100

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "UP"]

[tool.mypy]
python_version = "3.11"
```

### 2.2 提交规范

```
<type>(<scope>): <description>

Types:
- feat: 新功能
- fix: Bug 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建

Examples:
feat(scanner): 添加 PDF 解析
fix(indexer): 修复内存泄漏
```

---

## 3. Git 工作流

```
main (生产)
│
├── develop (开发)
│   ├── feature/*
│   ├── fix/*
│   └── chore/*
│
└── release/v0.1.0
```

---

## 4. API 设计规范

### 4.1 响应格式

```python
class ApiResponse(BaseModel):
    success: bool
    data: Any = None
    error: str = None
    meta: dict = None

class PaginatedResponse(ApiResponse):
    data: List[Any]
    meta: {
        "total": int,
        "page": int,
        "limit": int
    }
```

### 4.2 错误码

| 码 | 说明 |
|---|------|
| 400 | 参数错误 |
| 401 | 未授权 |
| 404 | 资源不存在 |
| 422 | 验证错误 |
| 500 | 服务器错误 |

---

## 5. 测试规范

### 5.1 测试覆盖率

- 核心模块: >80%
- API: >90%

### 5.2 测试用例示例

```python
def test_document_creation():
    doc = Document(title="测试")
    assert doc.id is not None
    assert doc.status == "pending"
```

---

## 6. 部署规范

### 6.1 Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install .
COPY . .
CMD ["uvicorn", "skyone_shuge.api.main:app", "--host", "0.0.0.0"]
```

### 6.2 环境变量

```bash
# .env.example
DATABASE_URL=sqlite:///./data/skyone.db
QDRANT_URL=http://localhost:6333
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-xxx
```

---

## 里程碑

| 里程碑 | 日期 | 状态 |
|-------|------|------|
| M1: 项目初始化 | 02-04 | 待开始 |
| M2: 文档扫描器 | 02-07 | 待开始 |
| M3: 索引管理 | 02-09 | 待开始 |
| M4: AI 分类 | 02-11 | 待开始 |
| M5: 搜索功能 | 02-13 | 待开始 |
| M6: 用户界面 | 02-16 | 待开始 |
| **MVP 发布** | **02-18** | **目标** |

---

**版本**: v0.3
**日期**: 2026-02-03
