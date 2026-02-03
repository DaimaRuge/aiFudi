# SkyOne Shuge MVP 代码 v0.9

**版本**: v0.9
**日期**: 2026-02-03
**主题**: MVP Phase 1 - 基础设施代码

---

## 代码结构

```
skyone-shuge/src/
├── skyone_shuge/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # 配置管理
│   │   └── database.py        # 数据库连接
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── document.py        # 文档模型
│   │   ├── category.py        # 分类模型
│   │   ├── tag.py             # 标签模型
│   │   └── document_tag.py    # 文档-标签关联
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI 应用入口
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── documents.py   # 文档 API
│   │       ├── categories.py  # 分类 API
│   │       ├── search.py      # 搜索 API
│   │       └── health.py       # 健康检查
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── scanner.py        # 文档扫描服务
│   │   ├── indexer.py        # 索引管理服务
│   │   └── classifier.py     # AI 分类服务
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── file.py          # 文件提取器
│   │
│   └── cli/
│       └── main.py           # CLI 入口
│
├── scripts/
│   └── init_db.py            # 数据库初始化
│
├── tests/
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

## 核心功能

### 已实现

1. **文档管理 API**
   - 文档列表 (分页/筛选/搜索)
   - 文档详情
   - 更新/删除文档
   - AI 分类接口

2. **分类管理 API**
   - 分类列表
   - 分类树
   - 创建/删除分类

3. **搜索 API**
   - 关键词搜索
   - 搜索建议

4. **文档扫描服务**
   - 多格式支持 (PDF/DOCX/PPTX/TXT/MD)
   - 元数据提取
   - 文件哈希去重

5. **AI 分类服务**
   - LLM 分类集成
   - 批量分类

### 依赖

```toml
# 核心依赖
fastapi >=0.109.0
sqlalchemy >=2.0.25
pydantic >=2.5.3
uvicorn >=0.27.0

# 数据库
aiosqlite >=0.19.0
redis >=5.0.1

# 向量数据库
qdrant-client >=1.7.0

# AI
langchain >=0.1.5

# 文档处理
pymupdf >=1.23.0
python-docx >=1.1.0
python-pptx >=0.6.23
```

## 使用方法

```bash
# 安装依赖
poetry install

# 初始化数据库
poetry run python scripts/init_db.py

# 运行开发服务器
poetry run uvicorn skyone_shuge.api.main:app --reload

# 运行 CLI
poetry run sky --help
```

## API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /health | 健康检查 |
| GET | /api/v1/documents | 文档列表 |
| GET | /api/v1/documents/{id} | 文档详情 |
| PUT | /api/v1/documents/{id} | 更新文档 |
| DELETE | /api/v1/documents/{id} | 删除文档 |
| GET | /api/v1/documents/{id}/classify | AI 分类 |
| GET | /api/v1/categories | 分类列表 |
| GET | /api/v1/categories/tree | 分类树 |
| GET | /api/v1/search | 搜索文档 |

## 下一步

- [ ] 集成 LLM API (OpenAI/Claude/智谱)
- [ ] 向量搜索集成 (Qdrant)
- [ ] 用户认证
- [ ] 前端 UI
- [ ] 同步服务

---

**作者**: AI Assistant
