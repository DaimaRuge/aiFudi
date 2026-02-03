# SkyOne Shuge v1.0 - 完整代码版本

**版本**: 1.0
**日期**: 2026-02-03
**状态**: 完整代码 🎉

---

## 代码结构

```
src/
├── skyone_shuge/              # 33 Python 文件
│   ├── __init__.py          # 包初始化
│   ├── api/                 # FastAPI 应用
│   │   ├── main.py           # 应用入口
│   │   ├── schemas.py        # Pydantic 模型
│   │   ├── routers/          # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── documents.py   # 文档 CRUD
│   │   │   ├── categories.py  # 分类管理
│   │   │   ├── search.py     # 搜索
│   │   │   ├── health.py    # 健康检查
│   │   │   └── auth.py       # 认证
│   │   └── __init__.py
│   │
│   ├── core/                # 核心模块
│   │   ├── config.py         # 配置
│   │   ├── database.py      # 数据库连接
│   │   ├── auth.py         # JWT 认证
│   │   └── __init__.py
│   │
│   ├── models/              # 数据模型
│   │   ├── __init__.py      # Document/Category/Tag/User
│   │   └── ...
│   │
│   ├── services/           # 业务逻辑
│   │   ├── scanner.py       # 文档扫描
│   │   ├── classifier.py    # AI 分类
│   │   └── __init__.py
│   │
│   └── utils/              # 工具函数
│       └── __init__.py
│
├── pyproject.toml           # Poetry 配置
├── README.md               # 项目说明
└── .env.example           # 环境变量模板
```

## 核心功能

### API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /health | 健康检查 |
| GET | /api/v1/documents | 文档列表 |
| GET | /api/v1/documents/{id} | 文档详情 |
| PUT | /api/v1/documents/{id} | 更新文档 |
| DELETE | /api/v1/documents/{id} | 删除文档 |
| POST | /api/v1/documents/{id}/classify | AI 分类 |
| GET | /api/v1/categories | 分类列表 |
| GET | /api/v1/categories/tree | 分类树 |
| GET | /api/v1/search | 搜索文档 |
| POST | /api/v1/auth/register | 用户注册 |
| POST | /api/v1/auth/login | 用户登录 |

### 数据模型

- **Document**: 文档主模型
- **Category**: 分类模型 (树形结构)
- **Tag**: 标签模型
- **User**: 用户模型

### 服务

- **DocumentScanner**: 文档扫描服务
  - 支持 PDF/DOCX/PPTX/TXT/MD/HTML
  - 自动提取元数据
  - 文件哈希去重

- **ClassifierService**: AI 分类服务
  - LLM 集成框架
  - 智能分类建议
  - 批量分类

## 运行方式

### 1. 安装依赖

```bash
cd skyone-shuge/src
pip install -e .
```

### 2. 配置环境

```bash
cp .env.example .env
# 编辑 .env，设置 API keys
```

### 3. 启动服务

```bash
uvicorn skyone_shuge.api.main:app --reload
```

### 4. 访问

- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 技术栈

- **语言**: Python 3.10+
- **框架**: FastAPI 0.109+
- **数据库**: SQLite + AsyncSQLAlchemy
- **AI**: OpenAI/Anthropic (框架支持)
- **认证**: JWT + bcrypt

## PRD 文档

包含 34 个 PRD 文档，涵盖 v0.1 到 v5.5 的完整迭代。

---

**作者**: AI Assistant
**版本**: 1.0.0
