# 个人终身学习数字读书系统 - MVP演示版

基于大模型Agent的个人知识操作系统，实现文档管理、知识检索和AI对话功能。

## 🚀 快速开始

### 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ 内存
- 10GB+ 磁盘空间

### 安装步骤

1. **克隆或下载项目**
```bash
git clone <repository-url>
cd lifelong-learning-demo
```

2. **设置API密钥（可选）**
```bash
export DEEPSEEK_API_KEY=your_api_key_here
```

3. **启动服务**
```bash
chmod +x start.sh
./start.sh
```

4. **访问应用**
- 前端界面: http://localhost:8501
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 停止服务
```bash
./stop.sh
```

## 📋 功能特性

### 1. 文档管理
- ✅ 支持PDF、DOCX、TXT、MD格式
- ✅ 自动文档解析和分块
- ✅ 文档元数据提取
- ✅ 文档列表和详情查看
- ✅ 文档删除功能

### 2. 知识检索
- ✅ 基于语义的向量搜索
- ✅ 相似度评分和排序
- ✅ 多文档联合检索
- ✅ 实时搜索响应

### 3. AI对话
- ✅ 基于检索增强生成（RAG）
- ✅ 上下文感知对话
- ✅ 回答来源追踪
- ✅ 会话历史管理

### 4. 系统管理
- ✅ 健康状态监控
- ✅ 系统统计信息
- ✅ 配置管理
- ✅ 日志记录

## 🏗️ 系统架构

### 技术栈
- **后端**: FastAPI + Python 3.11
- **前端**: Streamlit + React组件
- **向量数据库**: ChromaDB
- **Embedding模型**: BGE-small-zh（本地）
- **AI模型**: DeepSeek API（可选）
- **容器化**: Docker + Docker Compose

### 服务架构
```
用户浏览器
    ↓
Streamlit前端 (8501端口)
    ↓
FastAPI后端 (8000端口)
    ├── 文档解析服务
    ├── 向量检索服务
    ├── AI对话服务
    └── 用户管理服务
    ↓
ChromaDB向量数据库 (本地)
```

## 📁 项目结构

```
lifelong-learning-demo/
├── backend/                    # 后端服务
│   ├── main.py                # FastAPI主应用
│   ├── models.py              # 数据模型
│   ├── document_parser.py     # 文档解析器
│   ├── vector_store.py        # 向量数据库服务
│   ├── ai_service.py          # AI服务
│   ├── requirements.txt       # Python依赖
│   ├── Dockerfile            # Docker配置
│   └── uploads/              # 上传文件存储
├── frontend/                  # 前端应用
│   ├── app.py                # Streamlit应用
│   ├── requirements.txt      # Python依赖
│   └── Dockerfile           # Docker配置
├── docker-compose.yml        # Docker Compose配置
├── start.sh                  # 启动脚本
├── stop.sh                   # 停止脚本
└── README.md                 # 本文档
```

## 🔧 配置说明

### 环境变量
| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | 空（使用模拟服务） |
| `BACKEND_URL` | 后端API地址 | http://localhost:8000 |

### API端点

#### 文档管理
- `POST /api/v1/documents/upload` - 上传文档
- `GET /api/v1/documents` - 获取文档列表
- `GET /api/v1/documents/{id}` - 获取文档详情
- `DELETE /api/v1/documents/{id}` - 删除文档

#### 知识检索
- `POST /api/v1/search` - 搜索文档
- `POST /api/v1/knowledge/query` - 知识查询

#### AI对话
- `POST /api/v1/chat` - AI对话

#### 系统管理
- `GET /health` - 健康检查
- `GET /api/v1/system/stats` - 系统统计

## 🎯 使用示例

### 1. 上传文档
1. 访问 http://localhost:8501
2. 点击"文档管理"标签页
3. 选择PDF/DOCX/TXT文件上传
4. 等待文档解析完成

### 2. 搜索知识
1. 点击"知识检索"标签页
2. 输入搜索关键词
3. 查看相关文档片段

### 3. AI对话
1. 点击"AI对话"标签页
2. 输入您的问题
3. AI基于您的文档内容回答

## 🚨 故障排除

### 常见问题

#### 1. 服务启动失败
```bash
# 查看日志
docker-compose logs -f

# 重启服务
docker-compose down
docker-compose up --build -d
```

#### 2. 文档上传失败
- 检查文件格式是否支持（PDF/DOCX/TXT/MD）
- 检查文件大小（建议<10MB）
- 查看后端日志：`docker-compose logs backend`

#### 3. AI对话无响应
- 检查DEEPSEEK_API_KEY是否设置
- 检查网络连接
- 使用模拟服务测试：不设置API密钥

#### 4. 搜索无结果
- 确保已上传文档
- 检查文档解析状态
- 尝试不同的搜索关键词

### 日志查看
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看后端服务日志
docker-compose logs backend -f

# 查看前端服务日志
docker-compose logs frontend -f
```

## 📈 性能指标

### 系统要求
- **最小配置**: 2核CPU, 4GB内存
- **推荐配置**: 4核CPU, 8GB内存
- **存储要求**: 10GB+（取决于文档数量）

### 性能表现
- 文档解析: < 5秒（10页PDF）
- 向量搜索: < 1秒
- AI响应: < 3秒（使用API）
- 并发用户: 10+（演示环境）

## 🔮 未来扩展

### 计划功能
- [ ] 用户认证和权限管理
- [ ] 多用户支持
- [ ] 文档分类和标签
- [ ] 高级搜索过滤器
- [ ] 批量文档处理
- [ ] 离线模式支持
- [ ] 移动端适配
- [ ] API密钥管理
- [ ] 使用量统计

### 技术改进
- [ ] 数据库持久化（PostgreSQL）
- [ ] 缓存优化（Redis）
- [ ] 异步任务队列（Celery）
- [ ] 监控和告警
- [ ] 自动化测试
- [ ] CI/CD流水线

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📞 支持

如有问题或建议，请：
1. 查看 [Issues](https://github.com/your-repo/issues)
2. 提交新的Issue
3. 或通过邮件联系

---

**版本**: v0.1.0  
**最后更新**: 2026-03-19  
**状态**: MVP演示版