# 个人终身学习数字读书系统 - Python简化版

基于Python的简化版本，一个文件实现完整的文档管理、知识检索和AI对话功能。

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip 20.0+
- 2GB+ 内存
- 5GB+ 磁盘空间

### 一键启动
```bash
# 克隆或下载项目
cd lifelong-learning-python

# 运行启动脚本
python run.py
```

系统将自动：
1. 检查依赖
2. 安装Python包
3. 创建必要目录
4. 启动后端服务
5. 打开浏览器

### 手动启动
```bash
# 1. 安装依赖
pip install -r backend/requirements.txt

# 2. 启动服务
python backend/simple_app.py

# 3. 在另一个终端测试
python test_api.py
```

## 📋 功能特性

### 核心功能
- ✅ **文档上传**：支持PDF、DOCX、TXT、MD格式
- ✅ **文档解析**：自动提取文本内容并分块
- ✅ **向量搜索**：基于语义的智能搜索
- ✅ **AI对话**：基于文档内容的智能问答
- ✅ **系统管理**：文档列表、详情、删除

### 技术特点
- **单文件架构**：一个Python文件包含所有功能
- **本地运行**：无需外部服务，BGE模型本地运行
- **轻量级**：依赖少，启动快，资源占用低
- **易扩展**：模块化设计，易于添加新功能

## 🏗️ 系统架构

### 技术栈
- **Web框架**: FastAPI
- **向量数据库**: ChromaDB
- **Embedding模型**: BGE-small-zh（本地）
- **AI服务**: DeepSeek API（可选）或模拟服务
- **文档解析**: PyPDF2 + python-docx + unstructured

### 文件结构
```
lifelong-learning-python/
├── backend/
│   ├── simple_app.py      # 主应用（所有功能在一个文件）
│   └── requirements.txt   # Python依赖
├── test_documents/        # 测试文档
│   ├── 终身学习.txt
│   └── AI教育.txt
├── uploads/              # 上传文件存储
├── data/                 # 文档数据存储
├── chroma_data/         # 向量数据库存储
├── run.py               # 一键启动脚本
├── test_api.py          # API测试脚本
└── README.md            # 本文档
```

## 📖 使用指南

### 1. 启动服务
```bash
python run.py
```

### 2. 访问API
- **API根目录**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### 3. 使用API

#### 上传文档
```bash
curl -X POST -F "file=@test_documents/终身学习.txt" http://localhost:8000/api/upload
```

#### 列出文档
```bash
curl http://localhost:8000/api/documents
```

#### 搜索文档
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"query":"终身学习", "limit":5}' \
  http://localhost:8000/api/search
```

#### AI对话
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"什么是终身学习？"}' \
  http://localhost:8000/api/chat
```

#### 系统统计
```bash
curl http://localhost:8000/api/stats
```

### 4. 完整测试
```bash
python test_api.py
```

## 🔧 配置说明

### 环境变量
| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | 空（使用模拟服务） |

### API端点

#### 文档管理
- `POST /api/upload` - 上传文档
- `GET /api/documents` - 获取文档列表
- `GET /api/documents/{id}` - 获取文档详情
- `DELETE /api/documents/{id}` - 删除文档

#### 知识检索
- `POST /api/search` - 搜索文档

#### AI对话
- `POST /api/chat` - AI对话

#### 系统管理
- `GET /health` - 健康检查
- `GET /api/stats` - 系统统计

## 🎯 核心代码

### 主应用类
```python
class LifelongLearningApp:
    def __init__(self):
        # 初始化组件
        self.parser = SimpleDocumentParser()      # 文档解析
        self.vector_store = SimpleVectorStore()   # 向量存储
        self.ai_service = SimpleAIService()       # AI服务
        self.documents = {}                       # 文档存储
```

### 文档解析
```python
class SimpleDocumentParser:
    def parse(self, file_path, doc_type):
        if doc_type == "pdf":
            return self.parse_pdf(file_path)
        elif doc_type == "docx":
            return self.parse_docx(file_path)
        # ... 其他格式
```

### 向量搜索
```python
class SimpleVectorStore:
    def search(self, query, limit=10):
        query_embedding = self.get_embedding(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit
        )
        return formatted_results
```

### AI对话
```python
class SimpleAIService:
    def generate_response(self, context, question):
        if not self.client:  # 模拟服务
            return "基于文档内容，这是一个重要的学习主题。"
        # 使用DeepSeek API
        return ai_response
```

## 🚨 故障排除

### 常见问题

#### 1. 依赖安装失败
```bash
# 使用国内镜像
pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用conda
conda create -n lifelong python=3.11
conda activate lifelong
pip install -r backend/requirements.txt
```

#### 2. BGE模型下载慢
```bash
# 手动下载模型
git lfs install
git clone https://huggingface.co/BAAI/bge-small-zh-v1.5
# 然后设置环境变量
export SENTENCE_TRANSFORMERS_HOME=/path/to/models
```

#### 3. 端口被占用
```bash
# 修改端口
python backend/simple_app.py --port 8080

# 或杀死占用进程
lsof -ti:8000 | xargs kill -9
```

#### 4. 内存不足
```bash
# 减少分块大小
# 在simple_app.py中修改：
def chunk_text(self, text: str, chunk_size: int = 300):  # 从500改为300
```

### 日志查看
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 性能优化

### 内存优化
- **分块大小**: 默认500词，可根据内存调整
- **缓存策略**: 文档内容分块存储，按需加载
- **模型加载**: BGE模型首次加载较慢，后续使用缓存

### 速度优化
- **并行处理**: 文档解析和向量化可并行
- **增量更新**: 只处理新增或修改的文档
- **缓存结果**: 搜索和对话结果缓存

### 存储优化
- **压缩存储**: 文档内容压缩存储
- **索引优化**: 向量数据库定期优化
- **清理策略**: 自动清理临时文件

## 🔮 扩展开发

### 添加新功能
1. **新文档格式支持**
```python
def parse_new_format(self, file_path):
    # 实现新格式解析
    pass
```

2. **新搜索功能**
```python
def advanced_search(self, query, filters):
    # 实现高级搜索
    pass
```

3. **新AI功能**
```python
def summarize_document(self, doc_id):
    # 文档总结功能
    pass
```

### 集成外部服务
1. **云存储集成**
```python
class CloudStorage:
    def upload_to_cloud(self, file_path):
        # 集成阿里云OSS、腾讯云COS等
        pass
```

2. **多AI模型支持**
```python
class MultiAIService:
    def __init__(self):
        self.deepseek = DeepSeekService()
        self.openai = OpenAIService()
        self.local = LocalModelService()
```

3. **用户系统**
```python
class UserSystem:
    def register(self, username, password):
        # 用户注册登录
        pass
```

## 📝 开发指南

### 代码规范
- **类型提示**: 所有函数使用类型提示
- **错误处理**: 使用try-except处理异常
- **日志记录**: 关键操作记录日志
- **配置分离**: 配置参数集中管理

### 测试规范
```bash
# 单元测试
python -m pytest tests/

# API测试
python test_api.py

# 性能测试
python benchmark.py
```

### 部署指南
```bash
# 生产环境部署
# 1. 安装依赖
pip install -r backend/requirements.txt

# 2. 使用生产服务器
uvicorn backend.simple_app:main --host 0.0.0.0 --port 8000 --workers 4

# 3. 使用nginx反向代理
# nginx配置略

# 4. 使用supervisor管理进程
# supervisor配置略
```

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

**版本**: v1.0.0  
**最后更新**: 2026-03-19  
**状态**: 生产就绪