# 天一阁 PRD v3.0.9

**版本**: v3.0.9  
**日期**: 2026-03-21  
**阶段**: MVP + 前端 WebSocket 集成 + 知识库问答 Agent + 断点续传

---

## 📋 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v3.0.9 | 2026-03-21 | 前端 WebSocket 客户端 + 知识库问答 Agent + 断点续传 |
| v3.0.8 | 2026-03-19 | WebSocket 实时通信 + Agent RAG 工具 + 工作流编排 |
| v3.0.7 | 2026-03-17 | 异步任务队列 + Celery + Redis 架构 |
| v3.0.6 | 2026-03-16 | API 服务层完整实现 |
| v3.0.5 | 2026-03-10 | RAG 引擎与高级搜索实现 |
| v3.0.3 | 2026-03-07 | Agent 框架、文档解析器、工作流引擎 |

---

## 📅 本次迭代目标

### 核心交付物
- [ ] **前端 WebSocket 客户端**: React Hook 封装，实时接收任务进度
- [ ] **知识库问答 Agent**: 完整的 RAG 问答工作流实现
- [ ] **断点续传机制**: 文档处理失败后的恢复能力
- [ ] **部署文档完善**: 生产环境配置指南

---

## 🎯 一、前端 WebSocket 客户端

### 1.1 技术方案

| 组件 | 技术 | 说明 |
|------|------|------|
| WebSocket 客户端 | **原生 WebSocket API** | 浏览器原生支持 |
| 状态管理 | **Zustand** | 与现有状态管理保持一致 |
| 重连机制 | **指数退避算法** | 自动重连，最大间隔 30s |
| 心跳检测 | **Ping/Pong** | 每 30 秒发送心跳 |

### 1.2 React Hook 设计

```typescript
// hooks/useWebSocket.ts
interface UseWebSocketOptions {
  token: string;                    // JWT Token
  onMessage?: (data: WSMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  autoReconnect?: boolean;          // 默认 true
  reconnectInterval?: number;       // 基础间隔 1s
  maxReconnectInterval?: number;    // 最大间隔 30s
}

interface UseWebSocketReturn {
  isConnected: boolean;
  isConnecting: boolean;
  send: (message: WSMessage) => void;
  subscribe: (taskId: string) => void;
  unsubscribe: (taskId: string) => void;
}

function useWebSocket(options: UseWebSocketOptions): UseWebSocketReturn;
```

### 1.3 WebSocket Store

```typescript
// stores/websocketStore.ts
interface WebSocketState {
  isConnected: boolean;
  isConnecting: boolean;
  reconnectAttempts: number;
  
  // 任务订阅
  subscribedTasks: Set<string>;
  
  // 任务进度缓存
  taskProgress: Map<string, TaskProgress>;
  
  // Actions
  connect: (token: string) => void;
  disconnect: () => void;
  subscribeTask: (taskId: string) => void;
  unsubscribeTask: (taskId: string) => void;
  updateTaskProgress: (taskId: string, progress: TaskProgress) => void;
}

interface TaskProgress {
  taskId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;           // 0-100
  currentStep: string;        // 当前步骤描述
  message?: string;           // 状态消息
  result?: any;               // 完成结果
  error?: string;             // 错误信息
}
```

### 1.4 消息类型定义

```typescript
// types/websocket.ts
export enum WSMessageType {
  // 系统消息
  PING = 'ping',
  PONG = 'pong',
  AUTH = 'auth',
  AUTH_SUCCESS = 'auth_success',
  AUTH_FAILED = 'auth_failed',
  
  // 任务订阅
  SUBSCRIBE = 'subscribe',
  UNSUBSCRIBE = 'unsubscribe',
  
  // 任务进度
  TASK_CREATED = 'task_created',
  TASK_STARTED = 'task_started',
  TASK_PROGRESS = 'task_progress',
  TASK_COMPLETED = 'task_completed',
  TASK_FAILED = 'task_failed',
  TASK_CANCELLED = 'task_cancelled',
  
  // 文档处理
  DOC_UPLOADED = 'doc_uploaded',
  DOC_PARSING = 'doc_parsing',
  DOC_CHUNKING = 'doc_chunking',
  DOC_EMBEDDING = 'doc_embedding',
  DOC_INDEXING = 'doc_indexing',
  DOC_COMPLETED = 'doc_completed',
  DOC_FAILED = 'doc_failed'
}

export interface WSMessage {
  type: WSMessageType;
  timestamp: number;
  data?: any;
}
```

### 1.5 组件集成

```typescript
// components/TaskProgress.tsx
interface TaskProgressProps {
  taskId: string;
  showDetails?: boolean;
}

export function TaskProgress({ taskId, showDetails = true }: TaskProgressProps) {
  const { taskProgress, subscribeTask, unsubscribeTask } = useWebSocketStore();
  const progress = taskProgress.get(taskId);
  
  useEffect(() => {
    subscribeTask(taskId);
    return () => unsubscribeTask(taskId);
  }, [taskId]);
  
  return (
    <Progress 
      percent={progress?.progress || 0}
      status={getProgressStatus(progress?.status)}
      showInfo={showDetails}
    />
  );
}
```

---

## 🎯 二、知识库问答 Agent

### 2.1 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    KnowledgeQAAgent                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ 意图识别    │→│ 检索策略    │→│ 答案生成            │  │
│  │ Intent      │  │ Retrieval   │  │ Generation          │  │
│  │ Analyzer    │  │ Router      │  │ Engine              │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│         ↓                ↓                   ↓              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ 问题分类    │  │ RAGTool     │  │ LLM 回答           │  │
│  │ 路由决策    │  │ SearchTool  │  │ 引用溯源            │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Agent 配置

```python
# agents/knowledge_qa_agent.py
class KnowledgeQAAgentConfig(BaseModel):
    """知识库问答 Agent 配置"""
    
    # LLM 配置
    llm_model: str = "gpt-4"           # 默认模型
    temperature: float = 0.3           # 低温度，更确定性
    max_tokens: int = 2000             # 最大生成长度
    
    # 检索配置
    retrieval_strategy: str = "hybrid"  # hybrid/vector/keyword
    top_k: int = 5                     # 检索文档数
    score_threshold: float = 0.7       # 相关性阈值
    
    # 回答配置
    enable_citation: bool = True       # 启用引用溯源
    enable_streaming: bool = True      # 启用流式输出
    max_context_length: int = 4000     # 最大上下文长度
    
    # 意图分析
    enable_intent_analysis: bool = True
    intent_confidence_threshold: float = 0.6
```

### 2.3 意图识别

```python
class IntentType(str, Enum):
    """查询意图类型"""
    FACTUAL = "factual"           # 事实查询
    DEFINITION = "definition"     # 概念定义
    COMPARISON = "comparison"     # 对比分析
    PROCEDURE = "procedure"       # 步骤流程
    SUMMARY = "summary"           # 总结概括
    EXPLORATION = "exploration"   # 探索性查询
    CLARIFICATION = "clarification"  # 澄清/追问

class IntentAnalysisResult(BaseModel):
    """意图分析结果"""
    intent: IntentType
    confidence: float
    entities: List[Entity]
    suggested_retrieval_strategy: str
    needs_clarification: bool
    clarification_question: Optional[str]
```

### 2.4 回答生成

```python
class QAResponse(BaseModel):
    """问答响应"""
    answer: str                      # 生成的答案
    confidence: float                # 置信度
    sources: List[Source]            # 引用来源
    intent: IntentType               # 识别意图
    retrieved_documents: List[Doc]   # 检索到的文档
    processing_time_ms: int          # 处理耗时
    
class Source(BaseModel):
    """引用来源"""
    document_id: str
    document_title: str
    chunk_index: int
    content: str
    relevance_score: float
```

### 2.5 提示词模板

```python
KNOWLEDGE_QA_PROMPT = """你是一个专业的知识库问答助手。基于以下检索到的信息回答问题。

## 检索信息
{context}

## 用户问题
{question}

## 回答要求
1. 基于提供的检索信息回答问题
2. 如果信息不足，明确说明"根据现有资料无法确定"
3. 使用 [^n] 格式标注信息来源（n 为文档序号）
4. 保持简洁专业，避免冗长

## 回答格式
[你的回答内容]

**参考来源：**
[^1] [文档标题1]
[^2] [文档标题2]
"""
```

---

## 🎯 三、断点续传机制

### 3.1 问题背景

文档处理流程较长（上传→解析→切分→向量化→索引），任何步骤失败都需要从断点恢复，而不是重新开始。

### 3.2 状态持久化

```python
# models/document.py
class DocumentProcessingState(BaseModel):
    """文档处理状态（可持久化）"""
    
    document_id: str
    current_step: ProcessingStep      # 当前步骤
    step_status: StepStatus           # 步骤状态
    
    # 各步骤的中间结果
    uploaded_path: Optional[str]      # 上传文件路径
    parsed_content: Optional[str]     # 解析后的内容
    chunks: Optional[List[Chunk]]     # 切分后的块
    embedding_ids: Optional[List[str]]  # 向量 ID 列表
    indexed: bool = False             # 是否已索引
    
    # 失败信息
    failed_step: Optional[ProcessingStep]
    error_message: Optional[str]
    retry_count: int = 0              # 重试次数
    
    # 时间戳
    created_at: datetime
    updated_at: datetime

class ProcessingStep(str, Enum):
    UPLOAD = "upload"
    PARSE = "parse"
    CHUNK = "chunk"
    EMBED = "embed"
    INDEX = "index"
    COMPLETE = "complete"

class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
```

### 3.3 断点恢复逻辑

```python
# workflows/document_workflow.py
class DocumentWorkflowEngine:
    
    async def resume_processing(self, document_id: str) -> Task:
        """从断点恢复文档处理"""
        
        # 1. 加载保存的状态
        state = await self.load_state(document_id)
        
        # 2. 确定恢复点
        resume_step = self._determine_resume_step(state)
        
        # 3. 验证中间结果有效性
        if not await self._validate_intermediate_results(state, resume_step):
            # 回退到上一步
            resume_step = self._get_previous_step(resume_step)
        
        # 4. 创建恢复任务
        task = await self.create_resume_task(document_id, resume_step, state)
        
        return task
    
    def _determine_resume_step(self, state: DocumentProcessingState) -> ProcessingStep:
        """确定从哪一步恢复"""
        if state.step_status == StepStatus.FAILED:
            return state.failed_step
        elif state.step_status == StepStatus.COMPLETED:
            return self._get_next_step(state.current_step)
        else:
            return state.current_step
    
    async def _validate_intermediate_results(
        self, 
        state: DocumentProcessingState, 
        step: ProcessingStep
    ) -> bool:
        """验证中间结果是否有效"""
        validators = {
            ProcessingStep.PARSE: lambda s: s.uploaded_path and os.path.exists(s.uploaded_path),
            ProcessingStep.CHUNK: lambda s: s.parsed_content is not None,
            ProcessingStep.EMBED: lambda s: s.chunks is not None and len(s.chunks) > 0,
            ProcessingStep.INDEX: lambda s: s.embedding_ids is not None,
        }
        validator = validators.get(step)
        return validator(state) if validator else True
```

### 3.4 任务重试策略

```python
# tasks/document_tasks.py
@app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    exponential_backoff=True
)
def process_document_with_resume(self, document_id: str, resume_step: Optional[str] = None):
    """支持断点续传的文档处理任务"""
    
    try:
        engine = DocumentWorkflowEngine()
        
        if resume_step:
            # 从指定步骤恢复
            result = engine.resume_from_step(document_id, resume_step)
        else:
            # 全新处理
            result = engine.process_from_beginning(document_id)
        
        return result
        
    except RetryableException as exc:
        # 可重试异常，指数退避重试
        retry_count = self.request.retries
        countdown = 60 * (2 ** retry_count)  # 1min, 2min, 4min
        raise self.retry(exc=exc, countdown=countdown)
        
    except NonRetryableException as exc:
        # 不可重试异常，记录失败状态
        engine.mark_failed(document_id, str(exc))
        raise
```

---

## 🎯 四、部署文档完善

### 4.1 生产环境配置

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  # API 服务
  api:
    image: skyone-shuge:${VERSION:-latest}
    environment:
      - ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET=${JWT_SECRET}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  # Worker
  worker:
    image: skyone-shuge:${VERSION:-latest}
    command: celery -A core.celery_app worker -l info -Q documents,embeddings,index,notifications
    environment:
      - ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    deploy:
      replicas: 4
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
  
  # Flower 监控
  flower:
    image: skyone-shuge:${VERSION:-latest}
    command: celery -A core.celery_app flower --port=5555
    ports:
      - "5555:5555"
    environment:
      - REDIS_URL=${REDIS_URL}
```

### 4.2 环境变量配置

```bash
# .env.production
# 数据库
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/skyone

# Redis
REDIS_URL=redis://redis:6379/0

# 安全
JWT_SECRET=your-256-bit-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_EMBEDDING_MODEL=text-embedding-3-small
DEFAULT_CHAT_MODEL=gpt-4

# 向量数据库
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION=documents

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
CELERY_WORKER_CONCURRENCY=4

# 存储
UPLOAD_DIR=/data/uploads
MAX_UPLOAD_SIZE=100MB
```

### 4.3 Nginx 配置

```nginx
# nginx.conf
upstream api {
    server api:8000;
}

server {
    listen 80;
    server_name _;
    
    # API 代理
    location /api/ {
        proxy_pass http://api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket 支持
    location /ws/ {
        proxy_pass http://api/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
    
    # 静态文件
    location / {
        root /var/www/frontend;
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 📁 文件清单

### 前端文件
```
src/frontend/src/
├── hooks/
│   └── useWebSocket.ts          # WebSocket Hook
├── stores/
│   └── websocketStore.ts        # WebSocket 状态管理
├── types/
│   └── websocket.ts             # 类型定义
└── components/
    └── TaskProgress.tsx         # 任务进度组件
```

### 后端文件
```
src/skyone_shuge/
├── agents/
│   ├── knowledge_qa_agent.py    # 知识库问答 Agent
│   └── prompts/
│       └── knowledge_qa.py      # 问答提示词
├── models/
│   └── document.py              # 文档状态模型
└── workflows/
    └── document_workflow.py     # 断点续传逻辑
```

### 部署文件
```
├── docker-compose.prod.yml      # 生产环境配置
├── .env.production.example      # 环境变量示例
└── deployment/
    └── nginx.conf               # Nginx 配置
```

---

## 🎯 验收标准

| 功能 | 验收标准 | 优先级 |
|------|----------|--------|
| WebSocket 客户端 | 能连接、接收消息、自动重连、显示进度 | P0 |
| 知识库问答 | 能回答问题、显示引用、支持流式输出 | P0 |
| 断点续传 | 失败后可恢复、不重做已完成步骤 | P1 |
| 部署文档 | 生产配置完整、可一键部署 | P1 |
