
# SkyOne Shuge v3.0.1 - 自主 Agent 系统架构设计

**版本**: v3.0.1
**日期**: 2026-03-03
**迭代主题**: 自主 Agent 系统架构设计

---

## 📋 版本概述

v3.0.1 是 v3.0 下一代智能平台的第一个迭代，专注于**自主 Agent 系统的架构设计**。

---

## 🎯 本次迭代目标

| 目标 | 状态 |
|------|------|
| 设计自主 Agent 系统架构 | ✅ 进行中 |
| 定义 Agent 接口规范 | ⏳ 待开始 |
| 设计 Agent 执行引擎 | ⏳ 待开始 |
| 更新系统架构文档 | ⏳ 待开始 |

---

## 🏗️ 自主 Agent 系统架构设计

### 1. 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    SkyOne Agent System                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                    User Interface                       │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │ │
│  │  │  Agent Chat  │  │ Task Builder │  │ Monitor  │  │ │
│  │  └──────────────┘  └──────────────┘  └──────────┘  │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                   Agent Orchestrator                    │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │ │
│  │  │   Planner    │  │  Executor    │  │ Monitor  │  │ │
│  │  └──────────────┘  └──────────────┘  └──────────┘  │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                    Core Services                        │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │ │
│  │  │  Understanding│  │  Reasoning   │  │  Memory  │  │ │
│  │  └──────────────┘  └──────────────┘  └──────────┘  │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                    Tool Registry                        │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │ │
│  │  │  Web Search  │  │  Doc Reader  │  │  Writer  │  │ │
│  │  └──────────────┘  └──────────────┘  └──────────┘  │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2. 核心组件设计

#### 2.1 Agent 定义

```python
# ml/agent/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AgentConfig(BaseModel):
    """Agent 配置"""
    name: str = Field(..., description="Agent 名称")
    role: str = Field(..., description="Agent 角色")
    goal: str = Field(..., description="Agent 目标")
    tools: List[str] = Field(default_factory=list, description="可用工具")
    llm_config: Dict[str, Any] = Field(default_factory=dict, description="LLM 配置")
    memory_config: Dict[str, Any] = Field(default_factory=dict, description="记忆配置")


class AgentState(BaseModel):
    """Agent 状态"""
    agent_id: str
    current_task: Optional[str] = None
    current_step: int = 0
    total_steps: int = 0
    status: str = "idle"  # idle/planning/executing/finished/failed
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error: Optional[str] = None


class AgentResult(BaseModel):
    """Agent 执行结果"""
    success: bool
    output: Any
    steps: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    error: Optional[str] = None


class BaseAgent(ABC):
    """Agent 基类"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.state = AgentState(agent_id=f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.memory = []
        self.tools = {}
    
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
    async def execute_step(self, step: Dict[str, Any]) -&gt; Dict[str, Any]:
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
```

#### 2.2 Agent 编排器

```python
# ml/agent/orchestrator.py
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from .base import BaseAgent, AgentConfig, AgentResult


class AgentOrchestrator:
    """
    Agent 编排器
    
    负责管理和协调多个 Agent 的执行
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue = asyncio.Queue()
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.results: Dict[str, AgentResult] = {}
    
    def register_agent(self, agent_id: str, agent: BaseAgent):
        """
        注册 Agent
        
        Args:
            agent_id: Agent ID
            agent: Agent 实例
        """
        self.agents[agent_id] = agent
    
    async def submit_task(
        self,
        agent_id: str,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        priority: int = 0
    ) -&gt; str:
        """
        提交任务
        
        Args:
            agent_id: 目标 Agent ID
            task: 任务描述
            context: 上下文信息
            priority: 优先级 (0-10，越大越优先)
            
        Returns:
            任务 ID
        """
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        task_item = {
            "task_id": task_id,
            "agent_id": agent_id,
            "task": task,
            "context": context,
            "priority": priority,
            "submitted_at": datetime.now()
        }
        
        await self.task_queue.put((-priority, task_item))  # 负号用于升序排列实现降序
        return task_id
    
    async def process_tasks(self):
        """处理任务队列"""
        while True:
            priority, task_item = await self.task_queue.get()
            
            try:
                agent_id = task_item["agent_id"]
                agent = self.agents.get(agent_id)
                
                if not agent:
                    self.results[task_item["task_id"]] = AgentResult(
                        success=False,
                        output=None,
                        steps=[],
                        metadata={"task_id": task_item["task_id"]},
                        error=f"Agent {agent_id} not found"
                    )
                    continue
                
                # 创建任务
                async def execute_task():
                    result = await agent.execute(
                        task_item["task"],
                        task_item["context"]
                    )
                    self.results[task_item["task_id"]] = result
                
                task_obj = asyncio.create_task(execute_task())
                self.active_tasks[task_item["task_id"]] = task_obj
                
            finally:
                self.task_queue.task_done()
    
    async def get_result(self, task_id: str, timeout: int = 300) -&gt; Optional[AgentResult]:
        """
        获取任务结果
        
        Args:
            task_id: 任务 ID
            timeout: 超时时间（秒）
            
        Returns:
            AgentResult: 执行结果
        """
        if task_id in self.results:
            return self.results[task_id]
        
        # 等待结果
        start_time = datetime.now()
        while (datetime.now() - start_time).seconds &lt; timeout:
            if task_id in self.results:
                return self.results[task_id]
            await asyncio.sleep(0.5)
        
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
            return {
                "agent_id": agent_id,
                "state": agent.state.dict(),
                "config": agent.config.dict()
            }
        return None
```

#### 2.3 规划器

```python
# ml/agent/planner.py
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import json


class Step(BaseModel):
    """执行步骤"""
    step_id: str = Field(..., description="步骤 ID")
    step_type: str = Field(..., description="步骤类型")
    description: str = Field(..., description="步骤描述")
    tool: Optional[str] = Field(None, description="使用的工具")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="输入参数")
    depends_on: List[str] = Field(default_factory=list, description="依赖的步骤")


class Plan(BaseModel):
    """执行计划"""
    plan_id: str
    goal: str
    steps: List[Step]
    estimated_duration: Optional[int] = None  # 秒
    success_criteria: Optional[str] = None


class TaskPlanner:
    """
    任务规划器
    
    将复杂任务分解为可执行的步骤
    """
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    async def create_plan(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
        available_tools: Optional[List[str]] = None
    ) -&gt; Plan:
        """
        创建执行计划
        
        Args:
            goal: 目标描述
            context: 上下文信息
            available_tools: 可用工具列表
            
        Returns:
            Plan: 执行计划
        """
        # 构建提示词
        prompt = self._build_planning_prompt(goal, context, available_tools)
        
        # 调用 LLM 生成计划
        response = await self.llm_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一个专业的任务规划专家。请将目标分解为可执行的步骤。"},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # 解析响应
        plan_data = json.loads(response.choices[0].message.content)
        
        # 创建 Plan 对象
        steps = [Step(**step) for step in plan_data.get("steps", [])]
        
        return Plan(
            plan_id=f"plan_{hash(goal) % 1000000}",
            goal=goal,
            steps=steps,
            estimated_duration=plan_data.get("estimated_duration"),
            success_criteria=plan_data.get("success_criteria")
        )
    
    def _build_planning_prompt(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
        available_tools: Optional[List[str]] = None
    ) -&gt; str:
        """构建规划提示词"""
        prompt_parts = [f"目标: {goal}\n"]
        
        if context:
            prompt_parts.append(f"\n上下文: {json.dumps(context, ensure_ascii=False, indent=2)}\n")
        
        if available_tools:
            prompt_parts.append(f"\n可用工具: {', '.join(available_tools)}\n")
        
        prompt_parts.append("""
请将上述目标分解为可执行的步骤，并以 JSON 格式返回，格式如下：
{
  "steps": [
    {
      "step_id": "step_1",
      "step_type": "tool_use|thought|final",
      "description": "步骤描述",
      "tool": "工具名称（如果使用工具）",
      "inputs": {},
      "depends_on": []
    }
  ],
  "estimated_duration": 300,
  "success_criteria": "成功标准描述"
}
""")
        
        return "\n".join(prompt_parts)
    
    async def refine_plan(
        self,
        plan: Plan,
        feedback: str,
        context: Optional[Dict[str, Any]] = None
    ) -&gt; Plan:
        """
        优化执行计划
        
        Args:
            plan: 原始计划
            feedback: 反馈信息
            context: 上下文信息
            
        Returns:
            Plan: 优化后的计划
        """
        # 构建优化提示词
        prompt = f"""
原始计划: {plan.json()}

反馈: {feedback}

请根据反馈优化计划，返回相同格式的 JSON。
"""
        
        # 调用 LLM 优化计划
        response = await self.llm_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一个专业的任务规划专家。请根据反馈优化执行计划。"},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # 解析响应并返回新计划
        plan_data = json.loads(response.choices[0].message.content)
        steps = [Step(**step) for step in plan_data.get("steps", [])]
        
        return Plan(
            plan_id=f"{plan.plan_id}_refined",
            goal=plan.goal,
            steps=steps,
            estimated_duration=plan_data.get("estimated_duration"),
            success_criteria=plan_data.get("success_criteria")
        )
```

---

## 📐 数据模型设计

### 1. Agent 任务模型

```python
# models/agent.py
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
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
    status = Column(String, default="pending", index=True)  # pending/processing/completed/failed
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


class AgentExecutionLog(Base):
    """Agent 执行日志"""
    __tablename__ = "agent_execution_logs"
    
    id = Column(String, primary_key=True, index=True)
    task_id = Column(String, index=True, nullable=False)
    agent_id = Column(String, index=True, nullable=False)
    step_id = Column(String, index=True, nullable=True)
    log_type = Column(String, nullable=False)  # info/warning/error/debug
    message = Column(Text, nullable=False)
    data = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


class AgentToolCall(Base):
    """Agent 工具调用记录"""
    __tablename__ = "agent_tool_calls"
    
    id = Column(String, primary_key=True, index=True)
    task_id = Column(String, index=True, nullable=False)
    agent_id = Column(String, index=True, nullable=False)
    tool_name = Column(String, nullable=False)
    inputs = Column(JSON, default=dict)
    outputs = Column(JSON, default=dict)
    success = Column(Boolean, default=True)
    error = Column(Text, nullable=True)
    duration_ms = Column(Float, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)
```

---

## 🔄 今日进度

| 项目 | 状态 |
|------|------|
| 创建 v3.0.1 PRD 文档 | ✅ 已完成 |
| 设计自主 Agent 系统架构 | ✅ 已完成 |
| 定义 Agent 基类与接口 | ✅ 已完成 |
| 设计 Agent 编排器 | ✅ 已完成 |
| 实现任务规划器 | ✅ 已完成 |
| 设计数据模型 | ✅ 已完成 |

---

## 📝 待办事项

- [ ] 创建 v3.0.1 架构文档
- [ ] 实现 Agent 执行引擎
- [ ] 实现工具注册与调用系统
- [ ] 实现 Agent 记忆系统
- [ ] 创建 Agent 监控界面
- [ ] 编写 API 接口
- [ ] 编写前端页面

---

**版本**: v3.0.1  
**日期**: 2026-03-03
