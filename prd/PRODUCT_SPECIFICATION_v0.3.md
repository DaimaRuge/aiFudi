# SkyOne Shuge (天一阁) PRD v0.3
**版本日期**: 2026-02-03
**主题**: MVP 开发计划与任务拆分

---

## 1. MVP 定义

### 1.1 核心目标
构建最小可用产品，验证核心假设：
- 用户愿意使用 AI 自动分类和索引文档
- 本地优先架构可行
- 向量搜索提升检索体验

### 1.2 MVP 范围

| 模块 | 功能 | 优先级 | 预估工时 |
|-----|------|-------|---------|
| 文档扫描 | 基础扫描 (PDF/DOCX/MD) | P0 | 3 天 |
| 索引管理 | SQLite 存储与查询 | P0 | 2 天 |
| 搜索功能 | 关键词 + 向量搜索 | P0 | 2 天 |
| AI 分类 | 单分类体系 + LLM 调用 | P0 | 2 天 |
| 用户界面 | Web UI (基础功能) | P0 | 3 天 |
| 分类管理 | 创建/编辑/删除分类 | P1 | 1 天 |
| 元数据提取 | 基础字段提取 | P1 | 2 天 |
| 文件监控 | 增量扫描 | P2 | 1 天 |
| 多格式支持 | PPTX/XLSX/HTML | P2 | 1 天 |

### 1.3 MVP 排除

以下功能不在 MVP 范围：
- [ ] 云端同步 (LibIndex One)
- [ ] 多分类体系
- [ ] 项目级管理
- [ ] 教育模块
- [ ] 无涯子 (AI 认知引擎)
- [ ] 离线 AI (本地模型)
- [ ] 移动端

---

## 2. 开发任务拆分 (WBS)

### Phase 1: 基础设施 (3 天)

```
Phase 1: 基础设施
├── 1.1 项目初始化 (0.5 天)
│   ├── [ ] 创建 Git 仓库
│   ├── [ ] 配置 Poetry/Pyenv
│   ├── [ ] 设置 CI/CD (GitHub Actions)
│   └── [ ] 配置代码规范 (Black, Ruff, MyPy)
│
├── 1.2 目录结构 (0.5 天)
│   ├── skyone_shuge/
│   │   ├── core/          # 核心模块
│   │   ├── api/           # FastAPI
│   │   ├── cli/           # CLI
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务逻辑
│   │   ├── utils/         # 工具函数
│   │   └── __init__.py
│   ├── tests/
│   ├── docs/
│   └── scripts/
│
└── 1.3 基础框架 (2 天)
    ├── [ ] 配置 FastAPI 应用
    ├── [ ] 配置 SQLite 连接
    ├── [ ] 配置日志系统
    ├── [ ] 配置错误处理
    └── [ ] 编写基础测试
```

### Phase 2: 文档扫描器 (3 天)

```
Phase 2: 文档扫描器
├── 2.1 文件系统遍历 (0.5 天)
│   ├── [ ] 实现路径扫描
│   ├── [ ] 实现递归/非递归扫描
│   ├── [ ] 实现文件过滤 (glob)
│   └── [ ] 测试用例
│
├── 2.2 格式检测 (0.5 天)
│   ├── [ ] 扩展名检测
│   ├── [ ] MIME 类型检测
│   └── [ ] 文件哈希计算
│
├── 2.3 文档解析器 (1.5 天)
│   ├── [ ] PDF 解析器 (PyMuPDF)
│   ├── [ ] DOCX 解析器 (python-docx)
│   ├── [ ] Markdown 解析器 (CommonMark)
│   └── [ ] TXT 解析器
│
└── 2.4 元数据提取 (0.5 天)
    ├── [ ] 标题提取
    ├── [ ] 作者提取
    └── [ ] 基础字段提取
```

### Phase 3: 索引管理 (2 天)

```
Phase 3: 索引管理
├── 3.1 数据模型 (0.5 天)
│   ├── [ ] 定义 SQLAlchemy 模型
│   ├── [ ] 实现数据库迁移 (Alembic)
│   └── [ ] 创建初始化脚本
│
├── 3.2 CRUD 操作 (1 天)
│   ├── [ ] 创建文档
│   ├── [ ] 读取文档 (单条/列表)
│   ├── [ ] 更新文档
│   └── [ ] 删除文档
│
└── 3.3 查询引擎 (0.5 天)
    ├── [ ] 条件查询
    ├── [ ] 分页查询
    └── [ ] 排序查询
```

### Phase 4: AI 分类 (2 天)

```
Phase 4: AI 分类
├── 4.1 LLM 集成 (0.5 天)
│   ├── [ ] OpenAI 集成
│   ├── [ ] Claude 集成
│   └── [ ] 智谱 GLM 集成 (国产备选)
│
├── 4.2 分类服务 (1 天)
│   ├── [ ] 提示词工程
│   ├── [ ] 分类 API
│   └── [ ] 结果解析
│
└── 4.3 缓存优化 (0.5 天)
    ├── [ ] LLM 响应缓存
    └── [ ] 分类结果缓存
```

### Phase 5: 搜索功能 (2 天)

```
Phase 5: 搜索功能
├── 5.1 关键词搜索 (0.5 天)
    ├── [ ] 全文索引 (SQLite FTS5)
    └── [ ] 多字段搜索
│
├── 5.2 向量搜索 (1 天)
    ├── [ ] BGE 模型集成
    ├── [ ] Qdrant 集成
    └── [ ] 混合搜索 (关键词 + 向量)
│
└── 5.3 搜索 API (0.5 天)
    ├── [ ] 搜索接口
    ├── [ ] 分页/过滤
    └── [ ] 结果高亮
```

### Phase 6: 用户界面 (3 天)

```
Phase 6: 用户界面
├── 6.1 Web 前端 (2 天)
│   ├── [ ] React 项目初始化
│   ├── [ ] 文档列表页面
│   ├── [ ] 搜索页面
│   └── [ ] 分类管理页面
│
└── 6.2 API 集成 (1 天)
    ├── [ ] 文档列表 API
    ├── [ ] 搜索 API
    ├── [ ] 分类 API
    └── [ ] 文件上传/扫描 API
```

### Phase 7: 测试与优化 (2 天)

```
Phase 7: 测试与优化
├── 7.1 单元测试 (1 天)
│   ├── [ ] 核心模块测试 (>80% 覆盖率)
│   ├── [ ] API 测试
│   └── [ ] CLI 测试
│
└── 7.2 性能优化 (1 天)
    ├── [ ] 数据库索引优化
    ├── [ ] 向量检索优化
    └── [ ] 内存占用优化
```

---

## 3. 技术栈最终确认

### 3.1 后端技术栈

| 组件 | 技术选型 | 版本 | 备注 |
|-----|---------|------|------|
| 语言 | Python | 3.11+ | 生态丰富、开发效率 |
| 框架 | FastAPI | 0.109+ | 高性能、异步 |
| ORM | SQLAlchemy | 2.0+ | 类型安全 |
| 数据库 | SQLite | 3.45+ | MVP 阶段 |
| 向量库 | Qdrant | 1.8+ | 轻量、易用 |
| CLI | Typer | 0.9+ | 现代化 CLI |
| 测试 | pytest | 7.4+ | 生态完善 |
| LLM 框架 | LangChain | 0.1+ | 简化集成 |

### 3.2 前端技术栈

| 组件 | 技术选型 | 版本 | 备注 |
|-----|---------|------|------|
| 框架 | React | 18+ | 组件化 |
| 构建工具 | Vite | 5+ | 快速构建 |
| UI 组件 | Ant Design | 5+ | 丰富组件 |
| 状态管理 | Zustand | 4+ | 轻量 |
| HTTP 客户端 | Axios | 1+ | 易用 |
| 类型 | TypeScript | 5+ | 类型安全 |

### 3.3 开发工具

| 工具 | 用途 |
|-----|------|
| Black | 代码格式化 |
| Ruff | Lint + Import 排序 |
| MyPy | 类型检查 |
| pre-commit | Git Hooks |
| GitHub Actions | CI/CD |
| Docker | 容器化 |

---

## 4. 项目目录结构

```
skyone-shuge/
├── .github/
│   └── workflows/
│       ├── ci.yml          # CI 流程
│       └── release.yml      # 发版流程
│
├── .vscode/
│   ├── settings.json       # VS Code 配置
│   └── extensions.json     # 推荐插件
│
├── docs/
│   ├── architecture/        # 架构文档
│   ├── api/                 # API 文档
│   └── guides/              # 使用指南
│
├── scripts/
│   ├── init_db.py           # 初始化数据库
│   ├── seed_data.py         # 种子数据
│   └── run_tests.sh         # 测试脚本
│
├── skyone_shuge/
│   ├── __init__.py
│   │
│   ├── core/                # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py        # 配置管理
│   │   ├── database.py      # 数据库连接
│   │   ├── logging.py       # 日志配置
│   │   └── security.py      # 安全相关
│   │
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── document.py      # 文档模型
│   │   ├── category.py      # 分类模型
│   │   └── user.py          # 用户模型
│   │
│   ├── services/           # 业务逻辑
│   │   ├── __init__.py
│   │   ├── scanner.py      # 文档扫描
│   │   ├── indexer.py      # 索引管理
│   │   ├── classifier.py   # AI 分类
│   │   ├── search.py        # 搜索服务
│   │   └── metadata.py      # 元数据提取
│   │
│   ├── api/                # FastAPI 应用
│   │   ├── __init__.py
│   │   ├── main.py          # 应用入口
│   │   ├── deps.py          # 依赖注入
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── documents.py # 文档接口
│   │   │   ├── categories.py# 分类接口
│   │   │   └── search.py    # 搜索接口
│   │   └── schemas/         # Pydantic 模型
│   │
│   ├── cli/                # CLI 应用
│   │   ├── __init__.py
│   │   ├── main.py          # CLI 入口
│   │   ├── commands/
│   │   │   ├── __init__.py
│   │   │   ├── scan.py      # 扫描命令
│   │   │   ├── search.py    # 搜索命令
│   │   │   └── classify.py  # 分类命令
│   │   └── utils.py
│   │
│   ├── ml/                 # 机器学习模块
│   │   ├── __init__.py
│   │   ├── embedding.py     # 向量化
│   │   ├── llm.py          # LLM 集成
│   │   └── classifier.py    # AI 分类器
│   │
│   └── utils/              # 工具函数
│       ├── __init__.py
│       ├── file.py         # 文件操作
│       ├── text.py         # 文本处理
│       └── hash.py         # 哈希计算
│
├── frontend/               # 前端项目
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── pages/         # 页面
│   │   ├── stores/        # 状态
│   │   ├── api/           # API 调用
│   │   └── utils/        # 工具
│   ├── public/
│   └── package.json
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # pytest 配置
│   ├── unit/
│   │   ├── test_models/
│   │   ├── test_services/
│   │   └── test_api/
│   └── integration/
│       └── test_e2e/
│
├── .env.example           # 环境变量示例
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml         # Poetry 配置
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 5. 开发规范

### 5.1 代码规范

**Python:**

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "UP"]
ignore"]

[tool.m = ["E501ypy]
python_version = "3.11"
warn_return_any = true
```

**TypeScript:**

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "strict": true,
    "jsx": "react-jsx"
  }
}
```

### 5.2 Git 工作流

```
main (生产分支)
│
├── develop (开发分支)
│   ├── feature/document-scanner
│   ├── feature/index-management
│   ├── feature/ai-classification
│   └── feature/search-function
│
└── release/v0.1.0
```

**提交规范:**

```
<type>(<scope>): <description>

Types:
- feat: 新功能
- fix: Bug 修复
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试
- chore: 构建/工具

Examples:
feat(scanner): 添加 PDF 解析功能
fix(indexer): 修复内存泄漏问题
docs(api): 更新 API 文档
```

### 5.3 API 设计规范

```python
# 响应格式
class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    meta: Optional[Dict] = None

# 分页格式
class PaginatedResponse(ApiResponse):
    data: List[Any]
    meta: {
        "total": int,
        "page": int,
        "limit": int,
        "total_pages": int
    }

# 错误码
ERROR_CODES = {
    400: "请求参数错误",
    401: "未授权",
    404: "资源不存在",
    422: "验证错误",
    500: "服务器错误"
}
```

### 5.4 测试规范

```python
# 测试文件命名
tests/
├── unit/
│   ├── test_models/
│   │   └── test_document.py
│   └── test_services/
│       └── test_indexer.py
└── integration/
    └── test_api/
        └── test_documents.py

# 测试用例示例
def test_document_creation():
    """测试文档创建"""
    doc = Document(
        title="测试文档",
        file_path="/path/to/file.pdf"
    )
    assert doc.id is not None
    assert doc.status == "pending"
```

---

## 6. 里程碑

| 里程碑 | 内容 | 目标日期 | 状态 |
|-------|------|---------|------|
| M1 | 项目初始化完成 | 2026-02-04 | 待开始 |
| M2 | 文档扫描器完成 | 2026-02-07 | 待开始 |
| M3 | 索引管理完成 | 2026-02-09 | 待开始 |
| M4 | AI 分类完成 | 2026-02-11 | 待开始 |
| M5 | 搜索功能完成 | 2026-02-13 | 待开始 |
| M6 | 用户界面完成 | 2026-02-16 | 待开始 |
| M7 | 测试与优化完成 | 2026-02-18 | 待开始 |
| **MVP** | **MVP 发布** | **2026-02-18** | **目标** |

---

## 7. 资源估算

### 7.1 人力估算

| Phase | 人力 (人天) | 累计 |
|-------|------------|------|
| Phase 1: 基础设施 | 3 | 3 |
| Phase 2: 文档扫描器 | 3 | 6 |
| Phase 3: 索引管理 | 2 | 8 |
| Phase 4: AI 分类 | 2 | 10 |
| Phase 5: 搜索功能 | 2 | 12 |
| Phase 6: 用户界面 | 3 | 15 |
| Phase 7: 测试优化 | 2 | 17 |
| **合计** | **17** | |

### 7.2 基础设施估算

| 资源 | MVP 阶段 | 生产阶段 |
|-----|---------|---------|
| 开发机 | 本地 | 本地 |
| 测试服务器 | 本地/Docker | 2C4G 云服务器 |
| 数据库 | SQLite | PostgreSQL |
| 向量库 | Qdrant (本地) | Qdrant (云) |
| API 调用 | 付费额度内 | 按量付费 |

---

## 8. 风险与对策

| 风险 | 影响 | 概率 | 对策 |
|-----|------|-----|------|
| LLM API 成本超支 | 预算超支 | 中 | 设置使用限额、缓存响应 |
| 向量库性能问题 | 响应延迟 | 低 | 优化索引参数 |
| 格式解析兼容性问题 | 功能缺失 | 中 | 渐进式支持、增加测试覆盖 |
| 前端开发进度延迟 | 交付延期 | 中 | 简化 UI、优先核心功能 |

---

## 9. 后续迭代计划

### v0.4 (待定)
- [ ] 云端同步 (LibIndex One)
- [ ] 多分类体系
- [ ] 项目级管理
- [ ] 用户认证

### v0.5 (待定)
- [ ] 无涯子 (AI 认知引擎)
- [ ] 教育模块
- [ ] 移动端 App

---

**作者**: AI Assistant
**更新日期**: 2026-02-03
