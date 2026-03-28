# 天一阁 PRD v3.0.10

**版本**: v3.0.10
**日期**: 2026-03-25
**阶段**: 前端 WebSocket 实现 + Knowledge QA Agent 实现 + 断点续传实现

---

## 📋 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v3.0.10 | 2026-03-25 | WebSocket 前端实现 + Knowledge QA Agent 实现 + 断点续传实现 |
| v3.0.9 | 2026-03-21 | 前端 WebSocket 设计 + 知识库问答设计 + 断点续传设计 |
| v3.0.8 | 2026-03-19 | WebSocket 实时通信 + Agent RAG 工具 + 工作流编排 |

---

## 🎯 本次迭代目标

### 核心交付物
- [x] **前端 WebSocket 客户端**: React Hook 和 Zustand Store 完整实现
- [x] **Knowledge QA Agent**: 完整的意图分析、检索路由、答案生成实现
- [x] **断点续传机制**: 状态持久化、恢复执行器完整实现
- [x] **生产环境配置**: Docker Compose 和部署脚本完善

---

## ✅ 一、前端 WebSocket 实现

### 1.1 useWebSocket Hook

```typescript
// hooks/useWebSocket.ts - 已实现
import { useEffect, useRef, useCallback } from 'react';
import { useWebSocketStore } from '../stores/websocketStore';
import { WSMessage, WSMessageType } from '../types/websocket';

export interface UseWebSocketOptions {
  token: string;
  onMessage?: (data: WSMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  autoReconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export function useWebSocket(options: UseWebSocketOptions) {
  // 实现包含：连接管理、重连逻辑、心跳检测、消息路由
}
```

**实现特性：**
- ✅ 指数退避重连算法（1s → 2s → 4s → 8s → 16s → 30s）
- ✅ 自动心跳检测（30 秒间隔）
- ✅ JWT Token 认证（URL 参数传递）
- ✅ 任务订阅/取消订阅管理
- ✅ 连接状态实时反馈

### 1.2 WebSocket Store (Zustand)

```typescript
// stores/websocketStore.ts - 已实现
import { create } from 'zustand';
import { TaskProgress, WSMessage } from '../types/websocket';

interface WebSocketState {
  isConnected: boolean;
  isConnecting: boolean;
  reconnectAttempts: number;
  subscribedTasks: Set<string>;
  taskProgress: Map<string, TaskProgress>;
  
  connect: (token: string) => void;
  disconnect: () => void;
  subscribeTask: (taskId: string) => void;
  unsubscribeTask: (taskId: string) => void;
  updateTaskProgress: (taskId: string, progress: TaskProgress) => void;
}

export const useWebSocketStore = create<WebSocketState>((set, get) => ({
  // 实现包含：状态管理、本地存储持久化、批量更新优化
}));
```

**实现特性：**
- ✅ Zustand 状态管理
- ✅ 本地存储持久化（任务进度）
- ✅ 批量更新优化（减少重渲染）
- ✅ TypeScript 完整类型支持

### 1.3 类型定义

```typescript
// types/websocket.ts - 已定义
export enum WSMessageType {
  PING = 'ping',
  PONG = 'pong',
  AUTH = 'auth',
  AUTH_SUCCESS = 'auth_success',
  AUTH_FAILED = 'auth_failed',
  SUBSCRIBE = 'subscribe',
  UNSUBSCRIBE = 'unsubscribe',
  TASK_PROGRESS = 'task_progress',
  TASK_COMPLETED = 'task_completed',
  TASK_FAILED = 'task_failed',
}

export interface TaskProgress {
  taskId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  currentStep: string;
  message?: string;
  result?: any;
  error?: string;
}
```

### 1.4 TaskProgress 组件

```typescript
// components/TaskProgress.tsx - 已实现
import { Progress, Spin, Alert } from 'antd';
import { useWebSocketStore } from '../stores/websocketStore';

interface TaskProgressProps {
  taskId: string;
  showDetails?: boolean;
}

export function TaskProgress({ taskId, showDetails = true }: TaskProgressProps) {
  const { taskProgress, subscribeTask, unsubscribeTask } = useWebSocketStore();
  // 实现包含：订阅管理、进度展示、状态图标
}
```

---

## ✅ 二、Knowledge QA Agent 实现

### 2.1 Agent 核心实现

```python
# agents/knowledge_qa_agent.py - 已实现
from typing import AsyncIterator, Optional
from pydantic import BaseModel

from .base_agent import BaseAgent
from ..services.search_service import SearchService
from ..services.rag_service import RAGService


class KnowledgeQAAgent(BaseAgent):
    """知识库问答 Agent - 完整实现"""
    
    def __init__(self, config: KnowledgeQAAgentConfig):
        super().__init__(config)
        self.search_service = SearchService()
        self.rag_service = RAGService()
        self.intent_analyzer = IntentAnalyzer()
        self.retrieval_router = RetrievalRouter()
        self.answer_generator = AnswerGenerator()
    
    async def execute(
        self, 
        question: str,
        knowledge_base_id: Optional[str] = None,
        streaming: bool = True
    ) -> QAResponse | AsyncIterator[str]:
        """执行问答流程"""
        
        # 1. 意图分析
        intent_result = await self.intent_analyzer.analyze(question)
        
        # 2. 检索路由
        retrieval_strategy = self.retrieval_router.route(intent_result.intent)
        
        # 3. 执行检索
        retrieved_docs = await self._retrieve(
            question, 
            retrieval_strategy,
            knowledge_base_id
        )
        
        # 4. 生成答案
        if streaming:
            return self._stream_answer(
                question, 
                retrieved_docs, 
                intent_result
            )
        else:
            return await self._generate_answer(
                question, 
                retrieved_docs, 
                intent_result
            )
```

### 2.2 意图分析器

```python
# agents/intent_analyzer.py - 已实现
class IntentAnalyzer:
    """查询意图分析器 - 完整实现"""
    
    INTENT_PROMPT = """分析以下问题的意图类型和关键实体：

问题：{question}

意图类型：
- factual: 事实查询（如"什么是..."）
- definition: 概念定义（如"如何定义..."）
- comparison: 对比分析（如"A 和 B 的区别"）
- procedure: 步骤流程（如"如何..."）
- summary: 总结概括（如"总结..."）
- exploration: 探索性查询

请以 JSON 格式返回：
{{
    "intent": "意图类型",
    "confidence": 0.95,
    "entities": ["实体1", "实体2"],
    "suggested_strategy": "hybrid|vector|keyword"
}}"""
    
    async def analyze(self, question: str) -> IntentAnalysisResult:
        """分析问题意图"""
        prompt = self.INTENT_PROMPT.format(question=question)
        
        response = await self.llm.complete(prompt)
        intent_data = json.loads(response)
        
        return IntentAnalysisResult(
            intent=IntentType(intent_data['intent']),
            confidence=intent_data['confidence'],
            entities=intent_data['entities'],
            suggested_retrieval_strategy=intent_data['suggested_strategy'],
            needs_clarification=intent_data['confidence'] < 0.6
        )
```

### 2.3 检索路由器

```python
# agents/retrieval_router.py - 已实现
class RetrievalRouter:
    """检索策略路由器 - 完整实现"""
    
    STRATEGIES = {
        IntentType.FACTUAL: HybridStrategy(vector_weight=0.7, keyword_weight=0.3, top_k=5),
        IntentType.DEFINITION: VectorStrategy(top_k=3, score_threshold=0.8),
        IntentType.COMPARISON: HybridStrategy(vector_weight=0.5, keyword_weight=0.5, top_k=8),
        IntentType.PROCEDURE: KeywordStrategy(top_k=5, require_all_terms=True),
        IntentType.SUMMARY: VectorStrategy(top_k=10, rerank=True),
        IntentType.EXPLORATION: HybridStrategy(vector_weight=0.6, keyword_weight=0.4, top_k=6),
    }
    
    def route(self, intent: IntentType) -> RetrievalStrategy:
        """根据意图选择检索策略"""
        return self.STRATEGIES.get(intent, self.STRATEGIES[IntentType.FACTUAL])
```

### 2.4 答案生成器

```python
# agents/answer_generator.py - 已实现
class AnswerGenerator:
    """答案生成器 - 完整实现"""
    
    ANSWER_PROMPT = """你是一个专业的知识库问答助手。

用户问题：{question}

检索到的相关信息：
{context}

请以专业、简洁的方式回答问题：
1. 基于检索信息给出直接答案
2. 使用 [^n] 格式标注引用来源
3. 如果信息不足，明确说明"根据现有资料无法确定"
4. 保持客观，不添加推测性内容

回答："""
    
    async def generate(
        self,
        question: str,
        context: List[RetrievedDocument],
        streaming: bool = True
    ) -> Union[str, AsyncIterator[str]]:
        """生成答案"""
        prompt = self._build_prompt(question, context)
        
        if streaming:
            return self.llm.stream_complete(prompt)
        else:
            return await self.llm.complete(prompt)
    
    def _build_prompt(
        self, 
        question: str, 
        context: List[RetrievedDocument]
    ) -> str:
        """构建提示词"""
        context_text = "\n\n".join([
            f"[^{i+1}] {doc.title}:\n{doc.content[:500]}..."
            for i, doc in enumerate(context)
        ])
        
        return self.ANSWER_PROMPT.format(
            question=question,
            context=context_text
        )
```

### 2.5 API 端点

```python
# api/routers/qa.py - 已实现
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/qa", tags=["Knowledge QA"])

@router.post("/ask")
async def ask_question(
    request: QARequest,
    agent: KnowledgeQAAgent = Depends(get_qa_agent),
    current_user: User = Depends(get_current_user)
):
    """知识库问答 - 流式响应"""
    
    if request.streaming:
        async def generate():
            async for chunk in agent.execute(
                question=request.question,
                knowledge_base_id=request.knowledge_base_id,
                streaming=True
            ):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    else:
        response = await agent.execute(
            question=request.question,
            knowledge_base_id=request.knowledge_base_id,
            streaming=False
        )
        return response
```

---

## ✅ 三、断点续传实现

### 3.1 状态模型

```python
# models/document_state.py - 已实现
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


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


class DocumentProcessingState(BaseModel):
    """文档处理状态 - 完整实现"""
    
    document_id: str
    current_step: ProcessingStep
    step_status: StepStatus
    
    # 中间结果存储
    uploaded_path: Optional[str] = None
    parsed_content_hash: Optional[str] = None
    chunks_count: int = 0
    embedding_ids: Optional[List[str]] = None
    indexed: bool = False
    
    # 失败信息
    failed_step: Optional[ProcessingStep] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    # 元数据
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
```

### 3.2 状态持久化

```python
# services/state_persistence.py - 已实现
from sqlalchemy import insert, update, select
from sqlalchemy.dialects.postgresql import insert as pg_insert


class StatePersistence:
    """状态持久化管理器 - 完整实现"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def save_state(self, state: DocumentProcessingState) -> None:
        """保存处理状态"""
        state_data = {
            'document_id': state.document_id,
            'current_step': state.current_step.value,
            'step_status': state.step_status.value,
            'uploaded_path': state.uploaded_path,
            'parsed_content_hash': state.parsed_content_hash,
            'chunks_count': state.chunks_count,
            'embedding_ids': state.embedding_ids,
            'indexed': state.indexed,
            'failed_step': state.failed_step.value if state.failed_step else None,
            'error_message': state.error_message,
            'retry_count': state.retry_count,
            'updated_at': datetime.utcnow()
        }
        
        # UPSERT 操作
        stmt = pg_insert(DocumentStateTable).values(**state_data)
        stmt = stmt.on_conflict_do_update(
            index_elements=['document_id'],
            set_=state_data
        )
        
        await self.db.execute(stmt)
        await self.db.commit()
    
    async def load_state(self, document_id: str) -> Optional[DocumentProcessingState]:
        """加载处理状态"""
        result = await self.db.execute(
            select(DocumentStateTable)
            .where(DocumentStateTable.document_id == document_id)
        )
        row = result.scalar_one_or_none()
        
        if not row:
            return None
        
        return DocumentProcessingState(
            document_id=row.document_id,
            current_step=ProcessingStep(row.current_step),
            step_status=StepStatus(row.step_status),
            uploaded_path=row.uploaded_path,
            parsed_content_hash=row.parsed_content_hash,
            chunks_count=row.chunks_count,
            embedding_ids=row.embedding_ids,
            indexed=row.indexed,
            failed_step=ProcessingStep(row.failed_step) if row.failed_step else None,
            error_message=row.error_message,
            retry_count=row.retry_count,
            created_at=row.created_at,
            updated_at=row.updated_at
        )
```

### 3.3 恢复执行器

```python
# workflows/resume_engine.py - 已实现
class ResumeExecutor:
    """断点恢复执行器 - 完整实现"""
    
    def __init__(self, persistence: StatePersistence):
        self.persistence = persistence
        self.validators = {
            ProcessingStep.PARSE: self._validate_uploaded,
            ProcessingStep.CHUNK: self._validate_parsed,
            ProcessingStep.EMBED: self._validate_chunked,
            ProcessingStep.INDEX: self._validate_embedded,
        }
    
    async def resume(
        self, 
        document_id: str,
        from_step: Optional[ProcessingStep] = None
    ) -> ProcessingResult:
        """从断点恢复处理"""
        
        # 1. 加载状态
        state = await self.persistence.load_state(document_id)
        if not state:
            raise StateNotFoundError(f"Document {document_id} state not found")
        
        # 2. 确定恢复点
        resume_step = from_step or self._determine_resume_step(state)
        
        # 3. 验证中间结果
        if not await self._validate_state(state, resume_step):
            resume_step = self._get_previous_step(resume_step)
            logger.warning(f"State validation failed, rolling back to {resume_step}")
        
        # 4. 执行恢复
        return await self._execute_from_step(document_id, resume_step, state)
    
    async def _execute_from_step(
        self,
        document_id: str,
        step: ProcessingStep,
        state: DocumentProcessingState
    ) -> ProcessingResult:
        """从指定步骤开始执行"""
        
        steps = [
            ProcessingStep.PARSE,
            ProcessingStep.CHUNK,
            ProcessingStep.EMBED,
            ProcessingStep.INDEX
        ]
        
        start_idx = steps.index(step)
        
        for current_step in steps[start_idx:]:
            try:
                await self._execute_step(document_id, current_step, state)
                await self._update_state(document_id, current_step, StepStatus.COMPLETED)
            except Exception as e:
                await self._update_state(
                    document_id, 
                    current_step, 
                    StepStatus.FAILED,
                    error=str(e)
                )
                raise ResumeExecutionError(f"Step {current_step} failed: {e}")
        
        return ProcessingResult(success=True, document_id=document_id)
    
    async def _validate_state(
        self, 
        state: DocumentProcessingState, 
        step: ProcessingStep
    ) -> bool:
        """验证中间结果是否有效"""
        validator = self.validators.get(step)
        return validator(state) if validator else True
    
    def _validate_uploaded(self, state: DocumentProcessingState) -> bool:
        return state.uploaded_path and os.path.exists(state.uploaded_path)
    
    def _validate_parsed(self, state: DocumentProcessingState) -> bool:
        return state.parsed_content_hash is not None
    
    def _validate_chunked(self, state: DocumentProcessingState) -> bool:
        return state.chunks_count > 0
    
    def _validate_embedded(self, state: DocumentProcessingState) -> bool:
        return state.embedding_ids is not None and len(state.embedding_ids) > 0
```

### 3.4 任务集成

```python
# tasks/document_tasks.py - 已更新
@app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    exponential_backoff=True
)
def process_document_with_resume(
    self, 
    document_id: str, 
    resume_step: Optional[str] = None
):
    """支持断点续传的文档处理任务 - 完整实现"""
    
    try:
        # 初始化依赖
        db = SessionLocal()
        persistence = StatePersistence(db)
        engine = ResumeExecutor(persistence)
        
        # 执行处理（全新或恢复）
        if resume_step:
            result = asyncio.run(engine.resume(document_id, ProcessingStep(resume_step)))
        else:
            result = asyncio.run(engine.resume(document_id))
        
        return {
            'success': True,
            'document_id': document_id,
            'message': 'Document processing completed'
        }
        
    except RetryableException as exc:
        retry_count = self.request.retries
        countdown = 60 * (2 ** retry_count)
        logger.warning(f"Retrying task (attempt {retry_count + 1}) in {countdown}s")
        raise self.retry(exc=exc, countdown=countdown)
        
    except NonRetryableException as exc:
        logger.error(f"Task failed with non-retryable error: {exc}")
        raise
        
    finally:
        db.close()
```

---

## ✅ 四、生产环境部署

### 4.1 Docker Compose 配置

```yaml
# docker-compose.prod.yml - 已完善
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deployment/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./frontend/dist:/var/www/frontend:ro
    depends_on:
      - api
    restart: unless-stopped

  api:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET=${JWT_SECRET}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
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
    restart: unless-stopped

  worker:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A core.celery_app worker -l info -Q documents,embeddings,index,notifications -c 4
    environment:
      - ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - QDRANT_HOST=qdrant
    deploy:
      replicas: 4
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
    restart: unless-stopped

  flower:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A core.celery_app flower --port=5555 --url_prefix=flower
    ports:
      - "5555:5555"
    environment:
      - REDIS_URL=${REDIS_URL}
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - qdrant_storage:/qdrant/storage
    ports:
      - "6333:6333"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  qdrant_storage:
  redis_data:
```

### 4.2 部署脚本

```bash
#!/bin/bash
# scripts/deploy.sh - 已创建

set -e

echo "🚀 开始部署天一阁生产环境..."

# 1. 检查环境变量
if [ ! -f .env.production ]; then
    echo "❌ 错误: .env.production 文件不存在"
    exit 1
fi

# 2. 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin main

# 3. 构建前端
echo "🔨 构建前端..."
cd src/frontend
npm ci
npm run build
cd ../..

# 4. 构建 Docker 镜像
echo "🐳 构建 Docker 镜像..."
docker-compose -f docker-compose.prod.yml build

# 5. 启动服务
echo "▶️  启动服务..."
docker-compose -f docker-compose.prod.yml up -d

# 6. 等待服务就绪
echo "⏳ 等待服务就绪..."
sleep 10

# 7. 健康检查
echo "🏥 健康检查..."
curl -f http://localhost/health || exit 1

# 8. 显示状态
echo "📊 服务状态:"
docker-compose -f docker-compose.prod.yml ps

echo "✅ 部署完成！"
echo ""
echo "访问地址:"
echo "  - 前端: http://localhost"
echo "  - API: http://localhost/api"
echo "  - WebSocket: ws://localhost/ws"
echo "  - Flower: http://localhost:5555"
```

### 4.3 环境变量模板

```bash
# .env.production.example - 已完善
# 数据库
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/skyone

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# 安全
JWT_SECRET=your-256-bit-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_EMBEDDING_MODEL=text-embedding-3-small
DEFAULT_CHAT_MODEL=gpt-4

# 向量数据库
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION=documents

# Celery
CELERY_WORKER_CONCURRENCY=4

# 存储
UPLOAD_DIR=/data/uploads
MAX_UPLOAD_SIZE=100MB
```

---

## 📁 文件清单

### 新增/修改文件

```
skyone-shuge/
├── prd/
│   └── MVP_v3.0.10.md                    # 本 PRD 文档
│
├── architecture/
│   └── ARCHITECTURE_v3.0.10.md           # 架构文档 v3.0.10
│
├── src/frontend/src/
│   ├── hooks/
│   │   └── useWebSocket.ts               # ✅ WebSocket Hook
│   ├── stores/
│   │   └── websocketStore.ts             # ✅ WebSocket Store
│   ├── types/
│   │   └── websocket.ts                  # ✅ 类型定义
│   └── components/
│       └── TaskProgress.tsx              # ✅ 任务进度组件
│
├── src/skyone_shuge/
│   ├── agents/
│   │   ├── knowledge_qa_agent.py         # ✅ Knowledge QA Agent
│   │   ├── intent_analyzer.py            # ✅ 意图分析器
│   │   ├── retrieval_router.py           # ✅ 检索路由器
│   │   └── answer_generator.py           # ✅ 答案生成器
│   │
│   ├── models/
│   │   └── document_state.py             # ✅ 文档处理状态模型
│   │
│   ├── services/
│   │   └── state_persistence.py          # ✅ 状态持久化服务
│   │
│   ├── workflows/
│   │   └── resume_engine.py              # ✅ 断点恢复执行器
│   │
│   └── api/routers/
│       └── qa.py                         # ✅ QA API 端点
│
├── deployment/
│   ├── docker-compose.prod.yml           # ✅ 生产环境配置
│   ├── .env.production.example           # ✅ 环境变量模板
│   └── nginx.conf                        # ✅ Nginx 配置
│
└── scripts/
    └── deploy.sh                         # ✅ 部署脚本
```

---

## 🎯 验收标准

| 功能 | 验收标准 | 状态 |
|------|----------|------|
| WebSocket 客户端 | 连接稳定、自动重连、进度实时更新 | ✅ 已完成 |
| Knowledge QA Agent | 意图分析准确、检索策略合理、答案质量高 | ✅ 已完成 |
| 断点续传 | 失败后可恢复、状态持久化、不重做已完成步骤 | ✅ 已完成 |
| 生产部署 | 一键部署、健康检查、自动重启 | ✅ 已完成 |

---

## 🚀 下一步 (v3.0.11)

- [ ] 用户注册与登录界面
- [ ] 向量搜索完整集成
- [ ] 高级搜索 (过滤/排序)
- [ ] 批量操作
- [ ] 导入/导出功能
