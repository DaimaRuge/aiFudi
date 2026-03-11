
# SkyOne Shuge v3.0.1 - 自主 Agent 系统架构设计

**版本**: v3.0.1  
**日期**: 2026-03-03  
**描述**: 自主 Agent 系统的架构设计与技术实现方案

---

## 📋 概述

v3.0.1 专注于自主 Agent 系统的架构设计，定义了 Agent 的核心组件、接口规范和数据模型。

---

## 🏗️ 系统架构

### 1. 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SkyOne Shuge v3.0.1                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────┐    ┌──────────────────────────────────────┐  │
│  │   API Gateway        │    │         Web UI / CLI                  │  │
│  │  (FastAPI)           │    │     (Agent Chat / Task Monitor)      │  │
│  └──────────┬───────────┘    └─────────────────────┬────────────────┘  │
│             │                                          │                   │
│             └──────────────────┬───────────────────────┘                   │
│                                │                                           │
│  ┌─────────────────────────────▼──────────────────────────────────────┐  │
│  │                    Agent Orchestrator Service                        │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │  │
│  │  │  Task Queue      │  │  Agent Registry   │  │  Task Manager   │ │  │
│  │  └──────────────────┘  └──────────────────┘  └─────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                │                                           │
│  ┌─────────────────────────────┼──────────────────────────────────────┐  │
│  │                             │                                      │  │
│  │  ┌──────────────────────────▼──────────────────────────────────┐  │  │
│  │  │                     Agent Execution Engine                    │  │  │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │  │  │
│  │  │  │   Planner    │  │  Executor    │  │  Monitor         │ │  │  │
│  │  │  └──────────────┘  └──────────────┘  └──────────────────┘ │  │  │
│  │  └───────────────────────────────────────────────────────────────┘  │  │
│  │                                │                                       │  │
│  │  ┌─────────────────────────────┼───────────────────────────────────┐  │  │
│  │  │                             │                                   │  │  │
│  │  │  ┌──────────────────────────▼───────────────────────────────┐ │  │  │
│  │  │  │                    Core Services                           │ │  │  │
│  │  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │  │  │
│  │  │  │  │ Understanding│  │  Reasoning   │  │   Memory     │ │ │  │  │
│  │  │  │  └──────────────┘  └──────────────┘  └──────────────┘ │ │  │  │
│  │  │  └───────────────────────────────────────────────────────────┘ │  │  │
│  │  │                                │                                │  │  │
│  │  │  ┌─────────────────────────────┼─────────────────────────────┐ │  │  │
│  │  │  │                             │                              │ │  │  │
│  │  │  │  ┌──────────────────────────▼───────────────────────────┐ │ │  │  │
│  │  │  │  │                   Tool Registry                        │ │ │  │  │
│  │  │  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │ │ │  │  │
│  │  │  │  │  │  Web Search  │  │  Doc Reader  │  │  Writer  │  │ │ │  │  │
│  │  │  │  │  └──────────────┘  └──────────────┘  └──────────┘  │ │ │  │  │
│  │  │  │  └────────────────────────────────────────────────────────┘ │ │  │  │
│  │  │  └───────────────────────────────────────────────────────────────┘  │  │
│  │                                                                           │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                    │
│  ┌──────────────────────────────────────────────────────────────────────────────┐ │
│  │                                Data Layer                                      │ │
│  │  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐   │ │
│  │  │  PostgreSQL        │  │  Redis (Cache)     │  │  Vector DB         │   │ │
│  │  │  (Agent Tasks)     │  │  (Session / Queue) │  │  (Knowledge)       │   │ │
│  │  └────────────────────┘  └────────────────────┘  └────────────────────┘   │ │
│  └──────────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────────┘
```

### 2. 分层架构

#### 2.1 API 层 (API Layer)

**职责**:
- 提供 RESTful API 接口
- 处理 HTTP 请求与响应
- 认证与授权
- 请求验证与序列化

**主要组件**:
- `api/agent.py` - Agent API
- `api/tasks.py` - 任务管理 API
- `api/tools.py` - 工具管理 API

**接口设计**:

```python
# api/agent.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


class AgentCreateRequest(BaseModel):
    name: str
    role: str
    goal: str
    tools: Optional[List[str]] = None
    llm_config: Optional[dict] = None


class AgentResponse(BaseModel):
    agent_id: str
    name: str
    role: str
    goal: str
    status: str
    created_at: str


@router.post("", response_model=AgentResponse)
async def create_agent(request: AgentCreateRequest):
    """创建 Agent"""
    pass


@router.get("", response_model=List[AgentResponse])
async def list_agents():
    """列出所有 Agent"""
    pass


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """获取 Agent 详情"""
    pass


@router.post("/{agent_id}/tasks")
async def submit_task(agent_id: str, task: str, context: Optional[dict] = None):
    """提交任务给 Agent"""
    pass


@router.get("/{agent_id}/tasks/{task_id}")
async def get_task_status(agent_id: str, task_id: str):
    """获取任务状态"""
    pass
```

#### 2.2 服务层 (Service Layer)

**职责**:
- 业务逻辑处理
- Agent 生命周期管理
- 任务编排与执行
- 工具调用协调

**主要组件**:
- `services/agent_service.py` - Agent 服务
- `services/task_service.py` - 任务服务
- `services/orchestrator.py` - 编排器服务

#### 2.3 核心层 (Core Layer)

**职责**:
- Agent 核心逻辑实现
- 规划与推理引擎
- 记忆管理
- 工具抽象

**主要组件**:
- `ml/agent/base.py` - Agent 基类
- `ml/agent/orchestrator.py` - Agent 编排器
- `ml/agent/planner.py` - 任务规划器
- `ml/agent/memory.py` - 记忆系统

#### 2.4 数据层 (Data Layer)

**职责**:
- 数据持久化
- 缓存管理
- 向量存储

**主要组件**:
- `database/` - 数据库模型与连接
- `cache/` - 缓存管理
- `vectorstore/` - 向量存储

---

## 📦 核心模块设计

### 1. Agent 模块

#### 1.1 目录结构

```
ml/agent/
├── __init__.py
├── base.py              # Agent 基类与接口
├── orchestrator.py      # Agent 编排器
├── planner.py           # 任务规划器
├── executor.py          # 执行引擎
├── memory.py            # 记忆系统
├── tools.py             # 工具注册与调用
├── monitor.py           # 监控与日志
└── agents/              # 具体 Agent 实现
    ├── research_agent.py
    ├── writing_agent.py
    └── coding_agent.py
```

#### 1.2 Agent 基类 (base.py)

```python
# ml/agent/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class AgentConfig(BaseModel):
    """Agent 配置"""
    name: str = Field(..., description="Agent 名称")
    role: str = Field(..., description="Agent 角色")
    goal: str = Field(..., description="Agent 目标")
    description: Optional[str] = Field(None, description="Agent 描述")
    tools: List[str] = Field(default_factory=list, description="可用工具")
    llm_config: Dict[str, Any] = Field(default_factory=dict, description="LLM 配置")
    memory_config: Dict[str, Any] = Field(default_factory=dict, description="记忆配置")
    max_iterations: int = Field(100, description="最大迭代次数")
    timeout_seconds: int = Field(3600, description="超时时间（秒）")


class AgentState(BaseModel):
    """Agent 状态"""
    agent_id: str
    current_task_id: Optional[str] = None
    current_step: int = 0
    total_steps: int = 0
    status: str = "idle"  # idle/initializing/planning/executing/finished/failed
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error: Optional[str] = None
    iterations: int = 0


class StepResult(BaseModel):
    """步骤执行结果"""
    step_id: str
    step_type: str
    description: str
    success: bool
    output: Any = None
    error: Optional[str] = None
    duration_ms: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentResult(BaseModel):
    """Agent 执行结果"""
    success: bool
    task_id: str
    output: Any = None
    steps: List[StepResult] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None


class BaseAgent(ABC):
    """Agent 基类"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent_id = f"agent_{uuid.uuid4().hex[:12]}"
        self.state = AgentState(agent_id=self.agent_id)
        self.memory = []
        self.tools = {}
        self.step_results: List[StepResult] = []
    
    @abstractmethod
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -&gt; AgentResult:
        """
        执行任务
        
        Args:
            task: 任务描述
            context: 上下文信息
            
        Returns:
            AgentResult: 执行结果
        """
        pass
    
    @abstractmethod
    async def plan(self, task: str, context: Optional[Dict[str, Any]] = None) -&gt; List[Dict[str, Any]]:
        """
        制定执行计划
        
        Args:
            task: 任务描述
            context: 上下文信息
            
        Returns:
            执行计划列表
        """
        pass
    
    @abstractmethod
    async def execute_step(self, step: Dict[str, Any]) -&gt; StepResult:
        """
        执行单个步骤
        
        Args:
            step: 步骤定义
            
        Returns:
            步骤执行结果
        """
        pass
    
    def update_state(self, **kwargs):
        """更新 Agent 状态"""
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
    
    def add_step_result(self, result: StepResult):
        """添加步骤结果"""
        self.step_results.append(result)
    
    def get_state(self) -&gt; Dict[str, Any]:
        """获取 Agent 状态"""
        return {
            "agent_id": self.agent_id,
            "config": self.config.dict(),
            "state": self.state.dict(),
            "step_count": len(self.step_results)
        }
```

### 2. 编排器模块

#### 2.1 Agent 编排器 (orchestrator.py)

```python
# ml/agent/orchestrator.py
import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict
import heapq

from .base import BaseAgent, AgentConfig, AgentResult, AgentState


class TaskPriority:
    """任务优先级"""
    LOW = 0
    NORMAL = 5
    HIGH = 8
    URGENT = 10


class QueuedTask:
    """队列中的任务"""
    
    def __init__(
        self,
        task_id: str,
        agent_id: str,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        priority: int = TaskPriority.NORMAL
    ):
        self.task_id = task_id
        self.agent_id = agent_id
        self.task = task
        self.context = context or {}
        self.priority = priority
        self.submitted_at = datetime.utcnow()
    
    def __lt__(self, other):
        # 优先级高的先处理（使用负数实现最小堆）
        return (-self.priority, self.submitted_at) &lt; (-other.priority, other.submitted_at)


class AgentOrchestrator:
    """
    Agent 编排器
    
    负责管理和协调多个 Agent 的执行
    """
    
    def __init__(self, max_concurrent_tasks: int = 10):
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: List[QueuedTask] = []
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.results: Dict[str, AgentResult] = {}
        self.task_history: Dict[str, List[str]] = defaultdict(list)  # agent_id -&gt; task_ids
        self.max_concurrent_tasks = max_concurrent_tasks
        self._running = False
        self._queue_condition = asyncio.Condition()
    
    def register_agent(self, agent_id: str, agent: BaseAgent):
        """
        注册 Agent
        
        Args:
            agent_id: Agent ID
            agent: Agent 实例
        """
        self.agents[agent_id] = agent
        agent.agent_id = agent_id
    
    def unregister_agent(self, agent_id: str):
        """
        注销 Agent
        
        Args:
            agent_id: Agent ID
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
    
    async def submit_task(
        self,
        agent_id: str,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        priority: int = TaskPriority.NORMAL
    ) -&gt; str:
        """
        提交任务
        
        Args:
            agent_id: 目标 Agent ID
            task: 任务描述
            context: 上下文信息
            priority: 优先级
            
        Returns:
            任务 ID
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        
        queued_task = QueuedTask(
            task_id=task_id,
            agent_id=agent_id,
            task=task,
            context=context,
            priority=priority
        )
        
        async with self._queue_condition:
            heapq.heappush(self.task_queue, queued_task)
            self.task_history[agent_id].append(task_id)
            self._queue_condition.notify()
        
        return task_id
    
    async def start(self):
        """启动编排器"""
        if self._running:
            return
        
        self._running = True
        asyncio.create_task(self._process_tasks())
    
    async def stop(self):
        """停止编排器"""
        self._running = False
        async with self._queue_condition:
            self._queue_condition.notify_all()
        
        # 取消所有活动任务
        for task in self.active_tasks.values():
            task.cancel()
    
    async def _process_tasks(self):
        """处理任务队列"""
        while self._running:
            async with self._queue_condition:
                # 等待队列中有任务且不超过并发限制
                while (
                    self._running and
                    (len(self.task_queue) == 0 or
                     len(self.active_tasks) &gt;= self.max_concurrent_tasks)
                ):
                    await self._queue_condition.wait()
                
                if not self._running:
                    break
                
                # 获取最高优先级的任务
                if self.task_queue:
                    queued_task = heapq.heappop(self.task_queue)
                else:
                    continue
            
            # 创建并执行任务
            asyncio.create_task(self._execute_task(queued_task))
    
    async def _execute_task(self, queued_task: QueuedTask):
        """执行单个任务"""
        try:
            agent = self.agents.get(queued_task.agent_id)
            if not agent:
                self.results[queued_task.task_id] = AgentResult(
                    success=False,
                    task_id=queued_task.task_id,
                    error=f"Agent {queued_task.agent_id} not found"
                )
                return
            
            # 更新状态
            agent.update_state(
                status="executing",
                current_task_id=queued_task.task_id,
                started_at=datetime.utcnow()
            )
            
            # 执行任务
            result = await agent.execute(
                queued_task.task,
                queued_task.context
            )
            
            # 保存结果
            self.results[queued_task.task_id] = result
            
            # 更新状态
            agent.update_state(
                status="idle" if result.success else "failed",
                current_task_id=None,
                finished_at=datetime.utcnow()
            )
            
        except Exception as e:
            # 记录错误
            self.results[queued_task.task_id] = AgentResult(
                success=False,
                task_id=queued_task.task_id,
                error=str(e)
            )
            
            # 更新 Agent 状态
            agent = self.agents.get(queued_task.agent_id)
            if agent:
                agent.update_state(
                    status="failed",
                    error=str(e),
                    finished_at=datetime.utcnow()
                )
        
        finally:
            # 从活动任务中移除
            if queued_task.task_id in self.active_tasks:
                del self.active_tasks[queued_task.task_id]
            
            # 通知队列处理继续
            async with self._queue_condition:
                self._queue_condition.notify()
    
    async def get_result(
        self,
        task_id: str,
        timeout: int = 300,
        poll_interval: float = 0.5
    ) -&gt; Optional[AgentResult]:
        """
        获取任务结果
        
        Args:
            task_id: 任务 ID
            timeout: 超时时间（秒）
            poll_interval: 轮询间隔（秒）
            
        Returns:
            AgentResult: 执行结果
        """
        if task_id in self.results:
            return self.results[task_id]
        
        # 等待结果
        start_time = datetime.utcnow()
        while (datetime.utcnow() - start_time).total_seconds() &lt; timeout:
            if task_id in self.results:
                return self.results[task_id]
            await asyncio.sleep(poll_interval)
        
        return None
    
    def get_agent_status(self, agent_id: str) -&gt; Optional[Dict[str, Any]]:
        """
        获取 Agent 状态
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent 状态信息
        """
        agent = self.agents.get(agent_id)
        if agent:
            return agent.get_state()
        return None
    
    def list_agents(self) -&gt; List[Dict[str, Any]]:
        """列出所有 Agent"""
        return [
            {
                "agent_id": agent_id,
                "name": agent.config.name,
                "role": agent.config.role,
                "status": agent.state.status
            }
            for agent_id, agent in self.agents.items()
        ]
    
    def get_queue_status(self) -&gt; Dict[str, Any]:
        """获取队列状态"""
        return {
            "queued_tasks": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.results),
            "total_agents": len(self.agents)
        }
```

---

## 🗄️ 数据模型

### 1. 数据库模型

```python
# models/agent.py
from sqlalchemy import (
    Column, String, Text, Integer, Float, 
    DateTime, JSON, Boolean, ForeignKey, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class AgentTask(Base):
    """Agent 任务表"""
    __tablename__ = "agent_tasks"
    
    id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    task = Column(Text, nullable=False)
    context = Column(JSON, default=dict)
    status = Column(String, default="pending", index=True)
    priority = Column(Integer, default=0)
    
    # 执行信息
    plan = Column(JSON, default=dict)
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer, default=0)
    steps_log = Column(JSON, default=list)
    
    # 结果
    result = Column(JSON, default=dict)
    error = Column(Text, nullable=True)
    
    # 时间信息
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 索引
    __table_args__ = (
        Index('idx_agent_status', 'agent_id', 'status'),
        Index('idx_user_created', 'user_id', 'created_at'),
    )


class AgentExecutionLog(Base):
    """Agent 执行日志"""
    __tablename__ = "agent_execution_logs"
    
    id = Column(String, primary_key=True, index=True)
    task_id = Column(String, index=True, nullable=False)
    agent_id = Column(String, index=True, nullable=False)
    step_id = Column(String, index=True, nullable=True)
    log_type = Column(String, nullable=False, index=True)
    message = Column(Text, nullable=False)
    data = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_task_timestamp', 'task_id', 'timestamp'),
    )


class AgentToolCall(Base):
    """Agent 工具调用记录"""
    __tablename__ = "agent_tool_calls"
    
    id = Column(String, primary_key=True, index=True)
    task_id = Column(String, index=True, nullable=False)
    agent_id = Column(String, index=True, nullable=False)
    tool_name = Column(String, nullable=False, index=True)
    inputs = Column(JSON, default=dict)
    outputs = Column(JSON, default=dict)
    success = Column(Boolean, default=True, index=True)
    error = Column(Text, nullable=True)
    duration_ms = Column(Float, nullable=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_agent_tool', 'agent_id', 'tool_name'),
        Index('idx_task_success', 'task_id', 'success'),
    )
```

---

## 📊 技术栈

| 层级 | 技术选型 |
|------|----------|
| API 框架 | FastAPI |
| Agent 框架 | 自研（基于 LangChain 理念） |
| LLM | OpenAI GPT-4 / Claude 3 |
| 数据库 | PostgreSQL 15 |
| 缓存 | Redis 7 |
| 向量数据库 | Qdrant / PGVector |
| 消息队列 | Redis Queue / Celery |
| 监控 | Prometheus + Grafana |
| 日志 | ELK Stack |

---

## 🔄 今日进度

| 项目 | 状态 |
|------|------|
| 创建 v3.0.1 架构文档 | ✅ 已完成 |
| 设计系统整体架构 | ✅ 已完成 |
| 定义分层架构 | ✅ 已完成 |
| 实现 Agent 基类 | ✅ 已完成 |
| 实现 Agent 编排器 | ✅ 已完成 |
| 设计数据库模型 | ✅ 已完成 |

---

**版本**: v3.0.1  
**日期**: 2026-03-03