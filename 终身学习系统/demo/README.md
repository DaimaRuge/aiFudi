# 个人终身学习数字读书系统 MVP Demo

基于大模型 Agent 的智能学习生态系统，实现从信息管理到知识创造，再到个人成长的完整闭环。

## 🎯 核心功能

- **📚 文档管理**：支持 PDF、TXT、DOCX 文档的上传、解析和内容提取
- **🧠 知识图谱**：自动从文档中提取知识实体，构建知识网络
- **💬 AI 对话**：与文档内容进行智能对话，基于上下文回答问题
- **📈 学习路径**：AI 生成个性化学习路径，追踪学习进度

## 🏗️ 技术栈

### 后端
- **框架**：FastAPI (Python 3.11+)
- **数据库**：SQLite (开发环境)
- **认证**：JWT + OAuth2
- **AI**：OpenAI API / 模拟模式

### 前端
- **框架**：React 18 + TypeScript
- **UI 库**：Ant Design 5
- **路由**：React Router 6
- **可视化**：react-force-graph-2d

## 🚀 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- npm 或 yarn

### 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 http://localhost:8000 启动

API 文档地址：http://localhost:8000/docs

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
# 或
yarn install

# 启动开发服务器
npm start
# 或
yarn start
```

前端应用将在 http://localhost:3000 启动

## 📁 项目结构

```
demo/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   ├── auth.py        # 认证相关
│   │   │   ├── documents.py   # 文档管理
│   │   │   ├── knowledge.py   # 知识图谱
│   │   │   ├── chat.py        # AI 对话
│   │   │   └── learning.py    # 学习路径
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 应用配置
│   │   │   ├── database.py    # 数据库配置
│   │   │   └── security.py    # 安全认证
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic 模式
│   │   ├── services/          # 业务逻辑
│   │   │   ├── document_service.py
│   │   │   ├── ai_service.py
│   │   │   └── knowledge_service.py
│   │   └── main.py            # 应用入口
│   ├── uploads/               # 上传文件存储
│   └── requirements.txt       # Python 依赖
│
├── frontend/                   # 前端代码
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/        # 组件
│   │   │   └── Layout/
│   │   ├── hooks/             # 自定义 Hooks
│   │   ├── pages/             # 页面
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Documents.tsx
│   │   │   ├── KnowledgeGraph.tsx
│   │   │   ├── Chat.tsx
│   │   │   ├── LearningPaths.tsx
│   │   │   ├── Login.tsx
│   │   │   └── Register.tsx
│   │   ├── services/          # API 服务
│   │   ├── styles/            # 样式文件
│   │   ├── types/             # TypeScript 类型
│   │   ├── App.tsx            # 主应用
│   │   └── index.tsx          # 入口文件
│   ├── package.json
│   └── tsconfig.json
│
└── README.md
```

## 🔧 配置说明

### 环境变量

在后端目录创建 `.env` 文件：

```env
# 应用配置
DEBUG=true

# 数据库
DATABASE_URL=sqlite+aiosqlite:///./learning_system.db

# JWT
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# OpenAI (可选，不配置则使用模拟模式)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo
USE_MOCK_AI=true
```

前端可在 `.env` 文件中配置 API 地址：

```env
REACT_APP_API_URL=http://localhost:8000
```

## 📖 API 文档

### 认证 API

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| GET | `/api/auth/me` | 获取当前用户 |

### 文档 API

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/documents/upload` | 上传文档 |
| GET | `/api/documents` | 获取文档列表 |
| GET | `/api/documents/{id}` | 获取文档详情 |
| DELETE | `/api/documents/{id}` | 删除文档 |

### 知识图谱 API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/knowledge/graph` | 获取知识图谱 |
| GET | `/api/knowledge/graph/visualization` | 获取可视化数据 |
| GET | `/api/knowledge/search` | 搜索知识概念 |
| GET | `/api/knowledge/stats` | 获取统计信息 |

### 聊天 API

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/chat/sessions` | 创建会话 |
| GET | `/api/chat/sessions` | 获取会话列表 |
| GET | `/api/chat/sessions/{id}/messages` | 获取消息 |
| POST | `/api/chat/message` | 发送消息 |

### 学习路径 API

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/learning/paths` | 创建学习路径 |
| POST | `/api/learning/paths/generate` | AI 生成学习路径 |
| GET | `/api/learning/paths` | 获取学习路径列表 |
| GET | `/api/learning/paths/{id}` | 获取学习路径详情 |
| PUT | `/api/learning/paths/{pathId}/units/{unitId}/complete` | 完成学习单元 |

## 🔒 默认账户

首次使用需要注册账户。

## 🌟 功能演示

1. **注册/登录**：创建账户并登录系统
2. **上传文档**：上传 PDF、TXT 或 DOCX 文档
3. **查看知识图谱**：自动提取的知识网络可视化
4. **AI 对话**：与上传的文档内容进行对话
5. **学习路径**：使用 AI 生成个性化学习计划

## 📝 开发说明

### 添加新的 API

1. 在 `backend/app/api/` 创建新的路由文件
2. 在 `backend/app/main.py` 中注册路由
3. 在 `frontend/src/services/api.ts` 添加前端调用

### 添加新的页面

1. 在 `frontend/src/pages/` 创建页面组件
2. 在 `frontend/src/App.tsx` 添加路由

## 🚧 已知限制

- 使用 SQLite 作为开发数据库，生产环境建议使用 PostgreSQL
- 默认使用模拟 AI 模式，需要配置 OpenAI API Key 才能使用真实 AI 功能
- 知识图谱实体提取使用简化规则，生产环境建议使用专业 NLP 模型

## 📄 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**项目状态**：MVP Demo 已完成，可用于功能演示和进一步开发。
