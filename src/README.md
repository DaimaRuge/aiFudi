#天一阁 - README

# SkyOne Shuge (天一阁)

智能个人数字文献管理平台

## 功能特性

- 📄 **文档管理** - 支持 PDF、DOCX、PPTX、XLSX、Markdown 等格式
- 🤖 **AI 自动分类** - 基于 GPT-4/Claude 的智能分类
- 🔍 **语义搜索** - 支持关键词和向量语义搜索
- 🏷️ **智能标签** - 自动标签和手动标签
- 👤 **用户认证** - JWT Token 认证
- 📱 **跨平台** - Web API + CLI

## 快速开始

### 安装

```bash
git clone https://github.com/skyone-shuge/skyone-shuge.git
cd skyone-shuge

# 安装依赖
pip install -e .
```

### 配置

```bash
cp .env.example .env
# 编辑 .env 文件，设置 API keys
```

### 运行

```bash
# 启动 API 服务器
uvicorn skyone_shuge.api.main:app --reload

# 运行 CLI
sky scan /path/to/documents
```

### Docker

```bash
docker-compose up -d
```

## 项目结构

```
skyone_shuge/
├── api/              # FastAPI 应用
├── core/             # 配置和数据库
├── models/           # 数据模型
├── services/         # 业务逻辑
└── utils/            # 工具函数
```

## API 文档

启动服务后访问: http://localhost:8000/docs

## 许可证

MIT
