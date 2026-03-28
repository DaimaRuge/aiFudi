# 天一阁架构文档 v3.0.10

**版本**: v3.0.10
**日期**: 2026-03-25
**主题**: WebSocket 前端实现 + Knowledge QA Agent 实现 + 断点续传实现

---

## 📋 版本历史

| 版本 | 日期 | 主题 |
|------|------|------|
| v3.0.10 | 2026-03-25 | WebSocket 前端实现 + Knowledge QA Agent 实现 + 断点续传实现 |
| v3.0.9 | 2026-03-21 | WebSocket 设计 + 知识库问答设计 + 断点续传设计 |
| v3.0.8 | 2026-03-19 | WebSocket 实时通信 + 工作流编排 |

---

## 🏗️ 系统架构概览

### 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              前端层 (React/TypeScript)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ useWebSocket │  │ WebSocket    │  │ 状态管理     │  │ TaskProgress │   │
│  │ Hook         │  │ Store        │  │ Zustand      │  │ 组件         │   │
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
│  │  /auth  /documents  /search  /rag  /tasks  /analytics  /qa        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│  Knowledge QA Agent │  │    服务层           │  │    任务层 (Celery)  │
├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤
│ ├─ IntentAnalyzer   │  │ DocumentService     │  │ document_tasks      │
│ ├─ RetrievalRouter  │  │ SearchService       │  │ embedding_tasks     │
│ └─ AnswerGenerator  │  │ RAGService          │  │ index_tasks         │
│                     │  │ StatePersistence    │  │ notification_tasks  │
│                     │  │ ResumeExecutor      │  │                     │
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
│  │ + 状态表     │  │ Celery Broker│  │              │  │              │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 WebSocket 前端实现

### useWebSocket Hook 架构

```typescript
// hooks/useWebSocket.ts

class WebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectAttempts: number = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  
  // 状态
  private isConnected: boolean = false;
  private isConnecting: boolean = false;
  
  // 配置
  private readonly config: WSConfig = {
    baseUrl: 'ws://localhost/ws',
    autoReconnect: true,
    baseReconnectInterval: 1000,    // 1s
    maxReconnectInterval: 30000,    // 30s
    maxReconnectAttempts: 10,
    heartbeatInterval: 30000,       // 30s
    heartbeatTimeout: 10000         // 10s
  };
  
  // 指数退避算法
  private getReconnectDelay(): number {
    const delay = Math.min(
      this.config.baseReconnectInterval * Math.pow(2, this.reconnectAttempts),
      this.config.maxReconnectInterval
    );
    const jitter = Math.random() * 1000;
    return delay + jitter;
  }
  
  // 连接管理
  async connect(token: string): Promise<void> {
    if (this.isConnecting || this.isConnected) return;
    
    this.isConnecting = true;
    
    try {
      this.ws = new WebSocket(`${this.config.baseUrl}?token=${token}`);
      
      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      
    } catch (error) {
      this.handleConnectionError(error);
    }
  }
  
  // 消息处理
  private handleMessage(event: MessageEvent): void {
    try {
      const message: WSMessage = JSON.parse(event.data);
      
      switch (message.type) {
        case WSMessageType.PONG:
          this.handlePong();
          break;
        case WSMessageType.AUTH_SUCCESS:
          this.handleAuthSuccess();
          break;
        case WSMessageType.TASK_PROGRESS:
          this.handleTaskProgress(message.data);
          break;
        case WSMessageType.TASK_COMPLETED:
          this.handleTaskCompleted(message.data);
          break;
        case WSMessageType.TASK_FAILED:
          this.handleTaskFailed(message.data);
          break;
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }
  
  // 心跳机制
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected) {
        this.send({ type: WSMessageType.PING });
      }
    }, this.config.heartbeatInterval);
  }
  
  // 重连逻辑
  private scheduleReconnect(): void {
    if (!this.config.autoReconnect) return;
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      this.emit('maxReconnectExceeded');
      return;
    }
    
    const delay = this.getReconnectDelay();
    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      this.connect(this.token);
    }, delay);
  }
}
```

### WebSocket Store 状态管理

```typescript
// stores/websocketStore.ts

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface WebSocketState {
  // 连接状态
  isConnected: boolean;
  isConnecting: boolean;
  reconnectAttempts: number;
  lastConnectedAt: number | null;
  
  // 任务订阅
  subscribedTasks: Set<string>;
  
  // 任务进度缓存
  taskProgress: Map<string, TaskProgress>;
  
  // Actions
  setConnected: (connected: boolean) => void;
  setConnecting: (connecting: boolean) => void;
  incrementReconnectAttempts: () => void;
  resetReconnectAttempts: () => void;
  subscribeTask: (taskId: string) => void;
  unsubscribeTask: (taskId: string) => void;
  updateTaskProgress: (taskId: string, progress: TaskProgress) => void;
  clearTaskProgress: (taskId: string) => void;
}

export const useWebSocketStore = create<WebSocketState>()(
  persist(
    (set, get) => ({
      isConnected: false,
      isConnecting: false,
      reconnectAttempts: 0,
      lastConnectedAt: null,
      subscribedTasks: new Set(),
      taskProgress: new Map(),
      
      setConnected: (connected) => set({ 
        isConnected: connected,
        lastConnectedAt: connected ? Date.now() : get().lastConnectedAt
      }),
      
      setConnecting: (connecting) => set({ isConnecting: connecting }),
      
      incrementReconnectAttempts: () => set(state => ({
        reconnectAttempts: state.reconnectAttempts + 1
      })),
      
      resetReconnectAttempts: () => set({ reconnectAttempts: 0 }),
      
      subscribeTask: (taskId) => {
        const { subscribedTasks } = get();
        subscribedTasks.add(taskId);
        set({ subscribedTasks: new Set(subscribedTasks) });
      },
      
      unsubscribeTask: (taskId) => {
        const { subscribedTasks, taskProgress } = get();
        subscribedTasks.delete(taskId);
        taskProgress.delete(taskId);
        set({ 
          subscribedTasks: new Set(subscribedTasks),
          taskProgress: new Map(taskProgress)
        });
      },
      
      updateTaskProgress: (taskId, progress) => {
        const { taskProgress } = get();
        taskProgress.set(taskId, progress);
        set({ taskProgress: new Map(taskProgress) });
      },
      
      clearTaskProgress: (taskId) => {
        const { taskProgress } = get();
        taskProgress.delete(taskId);
        set({ taskProgress: new Map(taskProgress) });
      }
    }),
    {
      name: 'websocket-storage',
      partialize: (state) => ({
        // 只持久化任务进度
        taskProgress: Array.from(state.taskProgress.entries())
      })
    }
  )
);
```

### 重连策略状态机

```
                    ┌─────────────────┐
                    │    DISCONNECTED │
                    │    (初始状态)   │
                    └────────┬────────┘
                             │
                    connect()│
                             ▼
              ┌──────────────────────────┐
              │       CONNECTING         │
              │      (连接中...)         │
              └───────────┬──────────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
    ┌─────────────────┐     ┌─────────────────┐
    │    CONNECTED    │     │  CONNECT_ERROR  │
    │    (已连接)     │     │   (连接失败)    │
    └────────┬────────┘     └────────┬────────┘
             │                       │
             │              autoReconnect=true
             │                       │
             │              ┌────────▼────────┐
             │              │   RECONNECTING  │
             │              │  (等待重连...)  │
             │              │  delay = 2^n *  │
             │              │     baseDelay   │
             │              └────────┬────────┘
             │                       │
             │              maxAttempts
             │              exceeded?├────yes───▶ MAX_RECONNECT
             │                       │          (超过最大重试)
             │                       │no
             │                       ▼
             │              ┌─────────────────┐
             │              │   CONNECTING    │
             │              │   (再次连接)    │
             │              └─────────────────┘
             │
             │ onError / onClose
             │ (意外断开)
             ▼
    ┌─────────────────┐
    │  DISCONNECTED   │
    │   (已断开)      │
    └─────────────────┘
```

---

## 🤖 Knowledge QA Agent 架构

### Agent 处理流程

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        Knowledge QA Agent 流程                              │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────┐  │
│  │ 用户提问 │────▶│  意图分析    │────▶│  检索路由    │────▶│ 文档检索 │  │
│  │ Question │     │  Intent      │     │  Retrieval   │     │ Search   │  │
│  │          │     │  Analysis    │     │  Router      │     │          │  │
│  └──────────┘     └──────────────┘     └──────────────┘     └────┬─────┘  │
│                                                                  │        │
│                                                                  ▼        │
│  ┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────┐  │
│  │ 返回答案 │◀────│  答案生成    │◀────│  上下文构建  │◀────│ 结果处理 │  │
│  │ Response │     │  Answer      │     │  Context     │     │ Process  │  │
│  │          │     │  Generation  │     │  Building    │     │          │  │
│  └──────────┘     └──────────────┘     └──────────────┘     └──────────┘  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### 意图分析流程

```python
class IntentAnalyzer:
    """意图分析器架构"""
    
    def analyze(self, question: str) -> IntentAnalysisResult:
        """
        分析流程：
        
        1. LLM 意图分类
           ├── 事实查询 (factual)
           ├── 概念定义 (definition)
           ├── 对比分析 (comparison)
           ├── 步骤流程 (procedure)
           ├── 总结概括 (summary)
           └── 探索性查询 (exploration)
        
        2. 实体提取 (NER)
           ├── 专有名词
           ├── 技术术语
           └── 关键概念
        
        3. 置信度评估
           ├── 意图分类置信度
           ├── 实体识别置信度
           └── 综合置信度计算
        
        4. 检索策略推荐
           └── 根据意图类型推荐策略
        
        5. 澄清判断
           └── 置信度 < 0.6 时需要澄清
        """
```

### 检索策略矩阵

| 意图类型 | 向量权重 | 关键词权重 | Top K | 特殊处理 |
|----------|----------|------------|-------|----------|
| factual | 0.7 | 0.3 | 5 | 高相关性阈值 0.7 |
| definition | 1.0 | 0.0 | 3 | 语义相似度优先 |
| comparison | 0.5 | 0.5 | 8 | 扩展检索范围 |
| procedure | 0.3 | 0.7 | 5 | 关键词匹配优先 |
| summary | 0.8 | 0.2 | 10 | 重排序优化 |
| exploration | 0.6 | 0.4 | 6 | 平衡策略 |

### 答案生成流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      答案生成流程                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  输入: 问题 + 检索结果                                           │
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │ 上下文构建  │────▶│ 提示词组装  │────▶│ LLM 调用    │       │
│  │ Build       │     │ Build       │     │ Generate    │       │
│  │ Context     │     │ Prompt      │     │             │       │
│  └─────────────┘     └─────────────┘     └──────┬──────┘       │
│                                                  │              │
│                           ┌──────────────────────┘              │
│                           │                                     │
│                           ▼                                     │
│                  ┌─────────────────┐                           │
│                  │  流式输出?      │                           │
│                  │  streaming=true │                           │
│                  └────────┬────────┘                           │
│                           │                                     │
│            ┌──────────────┼──────────────┐                     │
│            │yes                          │no                   │
│            ▼                             ▼                     │
│  ┌─────────────────┐           ┌─────────────────┐             │
│  │  AsyncIterator  │           │  Complete       │             │
│  │  流式返回       │           │  完整返回       │             │
│  └─────────────────┘           └─────────────────┘             │
│                                                                 │
│  输出: 答案文本 + 引用来源 + 置信度                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 引用溯源机制

```python
class CitationTracker:
    """引用溯源追踪器"""
    
    def track_citations(
        self, 
        answer: str, 
        sources: List[RetrievedDocument]
    ) -> TrackedAnswer:
        """
        引用追踪流程：
        
        1. 在答案中检测 [^n] 标记
        2. 映射到对应的检索文档
        3. 验证引用的有效性
        4. 生成引用列表
        5. 计算整体置信度
        """
        
        citations = []
        citation_pattern = r'\[\^(\d+)\]'
        
        for match in re.finditer(citation_pattern, answer):
            idx = int(match.group(1)) - 1
            if 0 <= idx < len(sources):
                doc = sources[idx]
                citations.append(Citation(
                    index=idx + 1,
                    document_id=doc.id,
                    title=doc.title,
                    relevance_score=doc.score
                ))
        
        return TrackedAnswer(
            answer=answer,
            citations=citations,
            confidence=self._calculate_confidence(citations)
        )
```

---

## 💾 断点续传架构

### 状态持久化模型

```python
# 数据库表结构

class DocumentStateTable(Base):
    """文档处理状态表"""
    
    __tablename__ = 'document_processing_states'
    
    document_id = Column(String(36), primary_key=True)
    current_step = Column(String(20), nullable=False)  # ProcessingStep
    step_status = Column(String(20), nullable=False)   # StepStatus
    
    # 中间结果存储
    uploaded_path = Column(String(500))
    parsed_content_hash = Column(String(64))
    chunks_count = Column(Integer, default=0)
    embedding_ids = Column(JSON)  # List[str]
    indexed = Column(Boolean, default=False)
    
    # 失败信息
    failed_step = Column(String(20))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 索引
    __table_args__ = (
        Index('idx_status_step', 'step_status', 'current_step'),
        Index('idx_created_at', 'created_at'),
    )
```

### 状态机流程

```
                         ┌─────────────┐
                         │   UPLOAD    │
                         │  文件上传   │
                         └──────┬──────┘
                                │
                    success     │      fail
                        ┌───────┴───────┐
                        ▼               ▼
                 ┌─────────────┐   ┌─────────────┐
                 │    PARSE    │   │   FAILED    │
                 │  文档解析   │   │  失败状态   │
                 └──────┬──────┘   └──────┬──────┘
                        │                  │
           success      │      fail        │
               ┌────────┴────────┐         │
               ▼                 ▼         │
        ┌─────────────┐   ┌─────────────┐  │
        │   CHUNK     │   │   FAILED    │  │
        │  文本切分   │   │  (可恢复)   │  │
        └──────┬──────┘   └──────┬──────┘  │
               │                  │         │
               │         ┌────────┘         │
               │         │ resume           │
  success      │         ▼                  │
      ┌────────┴────────┐                   │
      ▼                 ▼                   │
┌─────────────┐   ┌─────────────┐           │
│   EMBED     │   │   PARSE     │◀──────────┘
│  向量化     │   │  (恢复点)   │
└──────┬──────┘   └─────────────┘
       │
       │success      fail
       │    ┌────────┴────────┐
       │    ▼                 ▼
       │┌─────────────┐   ┌─────────────┐
       ││   INDEX     │   │   CHUNK     │◀── 从失败点恢复
       ││  索引构建   │   │  (恢复点)   │
       │└──────┬──────┘   └─────────────┘
       │       │
       │       │success      fail
       │       │    ┌────────┴────────┐
       │       │    ▼                 ▼
       │       │┌─────────────┐   ┌─────────────┐
       │       ││  COMPLETE   │   │   EMBED     │◀── 从失败点恢复
       └───────┘│   完成     │   │  (恢复点)   │
                  └─────────────┘   └─────────────┘
```

### 恢复执行器架构

```python
class ResumeExecutor:
    """断点恢复执行器"""
    
    async def resume(self, document_id: str) -> ProcessingResult:
        """
        恢复执行流程：
        
        1. 加载状态
           └── 从数据库加载文档处理状态
        
        2. 确定恢复点
           ├── 如果状态为 FAILED → 从失败步骤恢复
           ├── 如果状态为 COMPLETED → 返回已完成
           └── 其他 → 从当前步骤继续
        
        3. 验证中间结果
           ├── 检查上传文件是否存在
           ├── 验证解析内容哈希
           ├── 检查切分块数量
           └── 验证向量 ID 列表
        
        4. 执行恢复
           ├── 从恢复点开始顺序执行
           ├── 每步完成后更新状态
           └── 失败时记录错误信息
        
        5. 完成处理
           ├── 更新文档状态为 COMPLETED
           └── 清理临时状态数据
        """
```

### 验证器链

```python
class StateValidatorChain:
    """状态验证链"""
    
    def __init__(self):
        self.validators: Dict[ProcessingStep, StateValidator] = {
            ProcessingStep.PARSE: UploadValidator(),
            ProcessingStep.CHUNK: ParseValidator(),
            ProcessingStep.EMBED: ChunkValidator(),
            ProcessingStep.INDEX: EmbedValidator(),
        }
    
    async def validate(
        self, 
        state: DocumentProcessingState, 
        target_step: ProcessingStep
    ) -> ValidationResult:
        """验证状态是否支持从目标步骤恢复"""
        
        # 获取验证器链
        chain = self._get_validator_chain(target_step)
        
        for validator in chain:
            result = await validator.validate(state)
            if not result.valid:
                return ValidationResult(
                    valid=False,
                    failed_at=validator.step,
                    reason=result.reason
                )
        
        return ValidationResult(valid=True)


class UploadValidator(StateValidator):
    """上传文件验证器"""
    
    async def validate(self, state: DocumentProcessingState) -> ValidatorResult:
        if not state.uploaded_path:
            return ValidatorResult(valid=False, reason="上传路径不存在")
        
        if not os.path.exists(state.uploaded_path):
            return ValidatorResult(valid=False, reason="上传文件不存在")
        
        # 验证文件完整性（可选）
        actual_hash = await self._calculate_file_hash(state.uploaded_path)
        if state.file_hash and actual_hash != state.file_hash:
            return ValidatorResult(valid=False, reason="文件哈希不匹配")
        
        return ValidatorResult(valid=True)


class ParseValidator(StateValidator):
    """解析结果验证器"""
    
    async def validate(self, state: DocumentProcessingState) -> ValidatorResult:
        if not state.parsed_content_hash:
            return ValidatorResult(valid=False, reason="解析内容未存储")
        
        # 从缓存或数据库加载解析内容验证
        content = await self._load_parsed_content(state.document_id)
        if not content:
            return ValidatorResult(valid=False, reason="解析内容无法加载")
        
        return ValidatorResult(valid=True)
```

---

## 🚀 生产部署架构

### 服务拓扑

```
                              ┌─────────────────┐
                              │   负载均衡器    │
                              │  Nginx/Traefik  │
                              │  SSL/路由/限流  │
                              └────────┬────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
              ▼                        ▼                        ▼
    ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
    │   API 实例 1    │      │   API 实例 2    │      │   API 实例 N    │
    │   (FastAPI)     │      │   (FastAPI)     │      │   (FastAPI)     │
    │                 │      │                 │      │                 │
    │  ┌───────────┐  │      │  ┌───────────┐  │      │  ┌───────────┐  │
    │  │ WebSocket │  │      │  │ WebSocket │  │      │  │ WebSocket │  │
    │  │  Manager  │  │      │  │  Manager  │  │      │  │  Manager  │  │
    │  └───────────┘  │      │  └───────────┘  │      │  └───────────┘  │
    └─────────────────┘      └─────────────────┘      └─────────────────┘
              │                        │                        │
              └────────────────────────┼────────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
          ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
          │   PostgreSQL    │ │     Redis       │ │     Qdrant      │
          │   (主从复制)    │ │  (Cluster模式)  │ │  (向量存储集群) │
          │                 │ │                 │ │                 │
          │ document_states │ │ Celery Broker   │ │ document_embeds │
          │ users/documents │ │  Cache          │ │                 │
          └─────────────────┘ └─────────────────┘ └─────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
          ┌─────────────────────────────────────────────────────┐
          │                 Celery Worker 集群                   │
          │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
          │  │   Worker 1  │ │   Worker 2  │ │   Worker N  │   │
          │  │  documents  │ │ embeddings  │ │    index    │   │
          │  └─────────────┘ └─────────────┘ └─────────────┘   │
          └─────────────────────────────────────────────────────┘
                                │
                                ▼
                      ┌─────────────────┐
                      │     Flower      │
                      │  (任务监控面板) │
                      │   port: 5555    │
                      └─────────────────┘
```

### 资源配置表

| 服务 | 实例数 | CPU | 内存 | 存储 | 说明 |
|------|--------|-----|------|------|------|
| Nginx | 2 | 1核 | 1GB | - | 负载均衡、SSL终止 |
| API | 2-4 | 2核 | 2GB | - | 水平扩展 |
| Worker | 4-8 | 4核 | 8GB | - | 根据队列负载调整 |
| PostgreSQL | 2 | 4核 | 8GB | 100GB SSD | 主从复制 |
| Redis | 3 | 2核 | 4GB | - | Cluster模式 |
| Qdrant | 3 | 4核 | 16GB | 500GB SSD | 向量索引 |
| Flower | 1 | 1核 | 1GB | - | 监控面板 |

### 健康检查配置

```yaml
# docker-compose.prod.yml 健康检查

services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
  
  worker:
    healthcheck:
      test: ["CMD-SHELL", "celery -A core.celery_app inspect ping || exit 1"]
      interval: 60s
      timeout: 10s
      retries: 3
    restart: unless-stopped
  
  qdrant:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
  
  redis:
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
```

---

## 📊 性能指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| WebSocket 连接延迟 | < 100ms | 建立连接到首次消息 |
| 任务进度推送延迟 | < 500ms | 状态变更到前端接收 |
| 问答首 token 延迟 | < 3s | 首次返回时间 |
| 问答完整响应时间 | < 10s | 完整答案生成时间 |
| 断点恢复时间 | < 1s | 状态加载和验证 |
| 文档处理吞吐量 | > 10 doc/min | 完整处理流程 |
| 系统可用性 | 99.9% | 年度目标 |

---

## 📁 文件清单

### 新增/修改文件

```
skyone-shuge/
├── architecture/
│   └── ARCHITECTURE_v3.0.10.md           # ✅ 本架构文档
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

## 🔐 安全考虑

### WebSocket 安全

1. **认证**: JWT Token 通过 URL 参数传递，服务端验证
2. **心跳**: 30 秒 ping/pong 检测连接有效性
3. **限流**: 单用户最多 5 个并发连接
4. **消息大小**: 限制单条消息最大 1MB
5. **CORS**: 严格限制允许的来源域名

### 断点续传安全

1. **状态验证**: 恢复前验证中间结果完整性（哈希校验）
2. **权限检查**: 恢复操作需验证用户文档所有权
3. **超时清理**: 超过 7 天的未完成状态自动清理
4. **加密存储**: 敏感状态数据加密存储

### 生产环境安全

1. **HTTPS**: 强制 HTTPS，HTTP 自动跳转
2. **Secrets**: 敏感配置通过环境变量注入
3. **网络隔离**: 数据库、缓存不暴露公网
4. **日志脱敏**: 用户敏感信息脱敏处理

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
