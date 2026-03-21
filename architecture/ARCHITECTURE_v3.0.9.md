# 天一阁架构文档 v3.0.9

**版本**: v3.0.9  
**日期**: 2026-03-21  
**主题**: 前端 WebSocket 集成 + 知识库问答 Agent + 断点续传

---

## 📋 版本历史

| 版本 | 日期 | 主题 |
|------|------|------|
| v3.0.9 | 2026-03-21 | 前端 WebSocket + 问答 Agent + 断点续传 |
| v3.0.8 | 2026-03-19 | WebSocket 实时通信 + 工作流编排 |
| v3.0.7 | 2026-03-17 | Celery 异步任务队列 |
| v3.0.6 | 2026-03-16 | API 服务层 |
| v3.0.5 | 2026-03-10 | RAG 引擎与搜索 |
| v3.0.3 | 2026-03-07 | Agent 框架 |

---

## 🏗️ 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              前端层 (React/TS)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ 页面组件     │  │ WebSocket    │  │ 状态管理     │  │ API 客户端   │   │
│  │ Pages        │  │ Client       │  │ Zustand      │  │ Axios        │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ WS / HTTP
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            API 层 (FastAPI)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     WebSocket 路由 (/ws)                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │ 连接管理器   │  │ 消息处理器   │  │ 认证中间件   │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        REST API 路由 (/api)                         │   │
│  │  /auth  /documents  /search  /rag  /tasks  /analytics               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│     Agent 层        │  │    服务层           │  │    任务层 (Celery)  │
├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤
│ KnowledgeQAAgent    │  │ DocumentService     │  │ document_tasks      │
│ ├─ 意图分析         │  │ SearchService       │  │ embedding_tasks     │
│ ├─ 检索路由         │  │ RAGService          │  │ index_tasks         │
│ └─ 答案生成         │  │ AgentService        │  │ notification_tasks  │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
              │                       │                       │
              └───────────────────────┼───────────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            基础设施层                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ PostgreSQL   │  │ Redis        │  │ Qdrant       │  │ FileSystem   │   │
│  │ 关系数据     │  │ 缓存/消息    │  │ 向量存储     │  │ 文件存储     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 WebSocket 客户端架构

### 连接生命周期

```
┌─────────────┐    connect()     ┌─────────────┐
│   初始化    │ ────────────────> │  连接中     │
└─────────────┘                   └─────────────┘
                                        │
                    onOpen              ▼
               ┌─────────────┐    ┌─────────────┐
               │   已连接    │ <───│  WebSocket  │
               └─────────────┘    └─────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   onMessage     onError      onClose
        │            │            │
        ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │消息处理 │  │错误处理 │  │重连判断 │
   └─────────┘  └─────────┘  └────┬────┘
                                  │
                    shouldReconnect = true
                                  │
                                  ▼
                           ┌─────────────┐
                           │ 指数退避    │
                           │ 重连等待    │
                           └──────┬──────┘
                                  │
                                  └────────> 连接中
```

### 重连策略

```typescript
// 指数退避算法
function getReconnectDelay(attempt: number): number {
  const baseDelay = 1000;           // 1 秒基础间隔
  const maxDelay = 30000;           // 30 秒最大间隔
  const jitter = Math.random() * 1000;  // 随机抖动
  
  const delay = Math.min(
    baseDelay * Math.pow(2, attempt),
    maxDelay
  );
  
  return delay + jitter;
}

// 重连流程
async function reconnect() {
  if (reconnectAttempts >= maxReconnectAttempts) {
    emit('maxReconnectExceeded');
    return;
  }
  
  const delay = getReconnectDelay(reconnectAttempts);
  await sleep(delay);
  
  reconnectAttempts++;
  await connect();
}
```

### 消息处理流程

```
┌─────────────────┐
│  WebSocket      │
│  onMessage      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  JSON 解析      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  消息路由       │────>│  PING/PONG      │
│  (switch type)  │     │  心跳处理       │
└────────┬────────┘     └─────────────────┘
         │
         ├──────────────> ┌─────────────────┐
         │                │  TASK_PROGRESS  │
         │                │  更新任务进度   │
         │                └─────────────────┘
         │
         ├──────────────> ┌─────────────────┐
         │                │  AUTH_*         │
         │                │  认证处理       │
         └────────────────┤                 │
                          └─────────────────┘
```

---

## 🤖 Knowledge QA Agent 架构

### 处理流程

```
┌────────────────────────────────────────────────────────────────┐
│                    知识库问答流程                               │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   │
│  │ 用户提问 │ → │ 意图分析 │ → │ 检索策略 │ → │ 执行检索 │   │
│  │ Question │   │ Intent   │   │ Router   │   │ Search   │   │
│  └──────────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   │
│                      │              │              │          │
│                      ▼              ▼              ▼          │
│                 ┌─────────┐   ┌──────────┐   ┌──────────┐    │
│                 │问题分类 │   │选择工具  │   │RAGTool/  │    │
│                 │实体提取 │   │调整参数  │   │SearchTool│    │
│                 └─────────┘   └──────────┘   └────┬─────┘    │
│                                                   │           │
│                                                   ▼           │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   │
│  │ 返回答案 │ ← │ 生成回答 │ ← │ 构建上下文│ ← │ 结果处理 │   │
│  │ Response │   │ Generate │   │ Context  │   │ Process  │   │
│  └──────────┘   └────┬─────┘   └────┬─────┘   └──────────┘   │
│                      │              │                         │
│                      ▼              ▼                         │
│                 ┌──────────┐   ┌──────────┐                  │
│                 │ LLM调用  │   │引用溯源  │                  │
│                 │ 流式输出 │   │置信度计算│                  │
│                 └──────────┘   └──────────┘                  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 意图分析模块

```python
class IntentAnalyzer:
    """查询意图分析器"""
    
    async def analyze(self, question: str) -> IntentAnalysisResult:
        """分析问题意图"""
        
        # 1. LLM 分析
        prompt = self._build_intent_prompt(question)
        response = await self.llm.complete(prompt)
        
        # 2. 解析结果
        intent_data = self._parse_intent_response(response)
        
        # 3. 实体提取
        entities = await self._extract_entities(question)
        
        # 4. 置信度评估
        confidence = self._calculate_confidence(intent_data, entities)
        
        return IntentAnalysisResult(
            intent=intent_data['intent'],
            confidence=confidence,
            entities=entities,
            suggested_retrieval_strategy=intent_data['strategy'],
            needs_clarification=confidence < self.clarification_threshold
        )
```

### 检索路由策略

```python
class RetrievalRouter:
    """检索策略路由器"""
    
    def route(self, intent: IntentType) -> RetrievalStrategy:
        """根据意图选择检索策略"""
        
        strategies = {
            IntentType.FACTUAL: HybridRetrieval(
                vector_weight=0.7,
                keyword_weight=0.3,
                top_k=5
            ),
            IntentType.DEFINITION: VectorRetrieval(
                top_k=3,
                score_threshold=0.8
            ),
            IntentType.COMPARISON: HybridRetrieval(
                vector_weight=0.5,
                keyword_weight=0.5,
                top_k=8
            ),
            IntentType.PROCEDURE: KeywordRetrieval(
                top_k=5,
                require_all_terms=True
            ),
            IntentType.SUMMARY: VectorRetrieval(
                top_k=10,
                rerank=True
            )
        }
        
        return strategies.get(intent, strategies[IntentType.FACTUAL])
```

### 答案生成模块

```python
class AnswerGenerator:
    """答案生成器"""
    
    async def generate(
        self,
        question: str,
        context: List[RetrievedDocument],
        intent: IntentType,
        streaming: bool = True
    ) -> Union[str, AsyncIterator[str]]:
        """生成答案"""
        
        # 1. 构建提示词
        prompt = self._build_answer_prompt(question, context, intent)
        
        # 2. 调用 LLM
        if streaming:
            return self._stream_answer(prompt, context)
        else:
            return await self._complete_answer(prompt, context)
    
    async def _stream_answer(
        self, 
        prompt: str, 
        context: List[RetrievedDocument]
    ) -> AsyncIterator[str]:
        """流式生成答案"""
        
        buffer = ""
        citation_buffer = []
        
        async for chunk in self.llm.stream_complete(prompt):
            buffer += chunk
            
            # 检测引用标记 [^n]
            if self._has_citation_marker(buffer):
                citation = self._extract_citation(buffer, context)
                citation_buffer.append(citation)
            
            yield chunk
        
        # 发送完整引用信息
        yield self._format_citations(citation_buffer)
```

---

## 💾 断点续传架构

### 状态机

```
                    ┌─────────────┐
                    │   UPLOAD    │
                    │  文件上传   │
                    └──────┬──────┘
                           │
              success      │      fail
                  ┌────────┴────────┐
                  ▼                 ▼
           ┌─────────────┐    ┌─────────────┐
           │    PARSE    │    │   FAILED    │
           │  文档解析   │    │   失败状态  │
           └──────┬──────┘    └─────────────┘
                  │
     success      │      fail
         ┌────────┴────────┐
         ▼                 ▼
  ┌─────────────┐    ┌─────────────┐
  │   CHUNK     │    │   FAILED    │
  │  文本切分   │    │ (可恢复)    │
  └──────┬──────┘    └──────┬──────┘
         │                   │
         │            resume │
         │                   ▼
success  │            ┌─────────────┐
    ┌────┴────┐       │   RESUME    │
    ▼         │       │  断点恢复   │
┌────────┐    │       └─────────────┘
│ EMBED  │    │
│向量化  │    │
└───┬────┘    │
    │         │
    │success  │fail
    │    ┌────┴────┐
    │    ▼         │
    │ ┌────────┐   │
    │ │ INDEX  │   │
    │ │ 索引   │   │
    │ └───┬────┘   │
    │     │        │
    │     │success │fail
    │     │   ┌────┴────┐
    │     │   ▼         │
    │     │┌─────────┐  │
    │     ││COMPLETE │  │
    │     ││ 完成   │  │
    └─────┘└─────────┘  └─────────────┘
```

### 状态持久化

```python
class StatePersistence:
    """状态持久化管理器"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def save_state(self, state: DocumentProcessingState):
        """保存处理状态"""
        
        # 序列化状态
        state_data = {
            'document_id': state.document_id,
            'current_step': state.current_step.value,
            'step_status': state.step_status.value,
            'uploaded_path': state.uploaded_path,
            'parsed_content_hash': self._hash_content(state.parsed_content),
            'chunks_count': len(state.chunks) if state.chunks else 0,
            'embedding_ids': state.embedding_ids,
            'indexed': state.indexed,
            'failed_step': state.failed_step.value if state.failed_step else None,
            'error_message': state.error_message,
            'retry_count': state.retry_count,
            'created_at': state.created_at.isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 保存到数据库
        await self.db.execute(
            insert(DocumentStateTable)
            .values(**state_data)
            .on_conflict_do_update(
                index_elements=['document_id'],
                set_=state_data
            )
        )
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
            # ... 其他字段
        )
```

### 恢复执行器

```python
class ResumeExecutor:
    """断点恢复执行器"""
    
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
        validation = await self._validate_state(state, resume_step)
        if not validation.valid:
            # 回退到有效步骤
            resume_step = validation.last_valid_step
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
        
        # 找到起始位置
        start_idx = steps.index(step)
        
        for current_step in steps[start_idx:]:
            try:
                result = await self._execute_step(document_id, current_step, state)
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
```

---

## 🚀 部署架构

### 生产环境拓扑

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              负载均衡层                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Nginx / Traefik                             │   │
│  │                    SSL 终止 / 路由 / 限流                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
          ▼                           ▼                           ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   API 实例 1    │         │   API 实例 2    │         │   API 实例 N    │
│   (FastAPI)     │         │   (FastAPI)     │         │   (FastAPI)     │
│                 │         │                 │         │                 │
│  ┌───────────┐  │         │  ┌───────────┐  │         │  ┌───────────┐  │
│  │ WebSocket │  │         │  │ WebSocket │  │         │  │ WebSocket │  │
│  │   Conn    │  │         │  │   Conn    │  │         │  │   Conn    │  │
│  └───────────┘  │         │  └───────────┘  │         │  └───────────┘  │
└─────────────────┘         └─────────────────┘         └─────────────────┘
          │                           │                           │
          └───────────────────────────┼───────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
          ┌─────────────────┐ ┌───────────────┐ ┌─────────────────┐
          │   PostgreSQL    │ │    Redis      │ │     Qdrant      │
          │   (主从复制)    │ │  (集群模式)   │ │  (向量存储)     │
          └─────────────────┘ └───────────────┘ └─────────────────┘
                    │                 │
                    │                 │
                    ▼                 ▼
          ┌─────────────────────────────────────────────┐
          │              Celery Worker 集群              │
          │  ┌─────────┐ ┌─────────┐ ┌─────────┐        │
          │  │ Worker 1│ │ Worker 2│ │ Worker N│        │
          │  │documents│ │embedding│ │  index  │        │
          │  └─────────┘ └─────────┘ └─────────┘        │
          └─────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │     Flower      │
                    │  (任务监控)     │
                    └─────────────────┘
```

### 资源规划

| 服务 | 实例数 | CPU | 内存 | 存储 | 说明 |
|------|--------|-----|------|------|------|
| API | 2 | 2核 | 2GB | - | 水平扩展 |
| Worker | 4 | 4核 | 8GB | - | 根据队列负载调整 |
| PostgreSQL | 2 | 4核 | 8GB | 100GB | 主从复制 |
| Redis | 3 | 2核 | 4GB | - | Cluster 模式 |
| Qdrant | 3 | 4核 | 16GB | 500GB | 向量索引 |
| Nginx | 2 | 1核 | 1GB | - | 负载均衡 |

---

## 📁 文件变更清单

### 新增文件

```
src/skyone_shuge/
├── agents/
│   ├── knowledge_qa_agent.py          # 知识库问答 Agent
│   └── prompts/
│       └── knowledge_qa.py            # 问答提示词
├── models/
│   └── document_state.py              # 文档处理状态模型
└── workflows/
    └── resume_engine.py               # 断点恢复引擎

src/frontend/src/
├── hooks/
│   └── useWebSocket.ts                # WebSocket React Hook
├── stores/
│   └── websocketStore.ts              # WebSocket 状态管理
├── types/
│   └── websocket.ts                   # WebSocket 类型定义
└── components/
    └── TaskProgress.tsx               # 任务进度组件

deployment/
├── docker-compose.prod.yml            # 生产环境 Docker Compose
├── .env.production.example            # 生产环境变量示例
└── nginx/
    └── nginx.conf                     # Nginx 配置文件
```

### 修改文件

```
src/skyone_shuge/
├── workflows/
│   └── document_workflow.py           # 集成断点续传逻辑
└── tasks/
    └── document_tasks.py              # 支持断点恢复的任务

src/frontend/src/
├── api/
│   └── index.ts                       # 添加 WebSocket 接口
└── stores/
    └── documentStore.ts               # 集成任务进度
```

---

## 🔐 安全考虑

### WebSocket 安全

1. **认证**: JWT Token 通过 URL 参数传递，服务端验证
2. **心跳**: 30 秒 ping/pong 检测连接有效性
3. **限流**: 单用户最多 5 个并发连接
4. **消息大小**: 限制单条消息最大 1MB

### 断点续传安全

1. **状态验证**: 恢复前验证中间结果完整性（哈希校验）
2. **权限检查**: 恢复操作需验证用户文档所有权
3. **超时清理**: 超过 7 天的未完成状态自动清理

---

## 📊 性能指标

| 指标 | 目标 | 说明 |
|------|------|------|
| WebSocket 连接延迟 | < 100ms | 建立连接到首次消息 |
| 任务进度推送延迟 | < 500ms | 状态变更到前端接收 |
| 问答响应时间 | < 3s | 首次 token 返回 |
| 断点恢复时间 | < 1s | 状态加载和验证 |
| 系统可用性 | 99.9% | 年度目标 |
