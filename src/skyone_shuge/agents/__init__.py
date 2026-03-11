"""
天一阁 - Agent 基类和注册中心
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Type
from enum import Enum
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent 状态"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class AgentType(Enum):
    """Agent 类型"""
    PROCESSING = "processing"  # 文档处理
    RETRIEVAL = "retrieval"    # 检索增强
    INTEGRATION = "integration" # 外部集成
    REASONING = "reasoning"     # 推理决策
    CONVERSATION = "conversation" # 对话


class BaseAgent(ABC):
    """
    Agent 基类
    
    所有专用 Agent 都应该继承此类，实现统一的接口。
    """
    
    # 子类必须定义的属性
    name: str = ""
    description: str = ""
    agent_type: AgentType = AgentType.PROCESSING
    version: str = "1.0.0"
    
    def __init__(self):
        self.status: AgentStatus = AgentStatus.IDLE
        self.last_run: Optional[datetime] = None
        self.error_count: int = 0
        self._context: Dict[str, Any] = {}
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行 Agent 的核心逻辑
        
        Args:
            input_data: 输入数据
            
        Returns:
            执行结果
        """
        pass
    
    async def __call__(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        让 Agent 可以像函数一样调用
        
        Args:
            input_data: 输入数据
            
        Returns:
            执行结果
        """
        return await self.run(input_data)
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行 Agent，包含状态管理和错误处理
        
        Args:
            input_data: 输入数据
            
        Returns:
            执行结果
        """
        self.status = AgentStatus.RUNNING
        self.last_run = datetime.utcnow()
        
        try:
            result = await self.execute(input_data)
            self.status = AgentStatus.IDLE
            self.error_count = 0
            return result
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.error_count += 1
            logger.error(f"Agent {self.name} 执行失败: {e}")
            raise
    
    async def pause(self):
        """暂停 Agent"""
        if self.status == AgentStatus.RUNNING:
            self.status = AgentStatus.PAUSED
            logger.info(f"Agent {self.name} 已暂停")
    
    async def resume(self):
        """恢复 Agent"""
        if self.status == AgentStatus.PAUSED:
            self.status = AgentStatus.IDLE
            logger.info(f"Agent {self.name} 已恢复")
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取 Agent 状态
        
        Returns:
            状态信息字典
        """
        return {
            "name": self.name,
            "type": self.agent_type.value,
            "status": self.status.value,
            "version": self.version,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "error_count": self.error_count,
        }
    
    def set_context(self, key: str, value: Any):
        """设置上下文"""
        self._context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """获取上下文"""
        return self._context.get(key, default)


class AgentRegistry:
    """
    Agent 注册中心
    
    管理所有可用的 Agent，支持动态注册和发现。
    """
    
    _agents: Dict[str, Type[BaseAgent]] = {}
    _instances: Dict[str, BaseAgent] = {}
    
    @classmethod
    def register(cls, agent_class: Type[BaseAgent]) -> Type[BaseAgent]:
        """
        注册一个 Agent 类
        
        可以作为装饰器使用:
            @AgentRegistry.register
            class MyAgent(BaseAgent):
                ...
        """
        if not agent_class.name:
            raise ValueError(f"Agent {agent_class.__name__} 必须定义 name 属性")
        
        cls._agents[agent_class.name] = agent_class
        logger.info(f"Agent 已注册: {agent_class.name}")
        return agent_class
    
    @classmethod
    def get_agent_class(cls, name: str) -> Optional[Type[BaseAgent]]:
        """获取 Agent 类"""
        return cls._agents.get(name)
    
    @classmethod
    def get_agent(cls, name: str) -> Optional[BaseAgent]:
        """获取或创建 Agent 实例（单例）"""
        if name in cls._instances:
            return cls._instances[name]
        
        agent_class = cls.get_agent_class(name)
        if agent_class:
            agent = agent_class()
            cls._instances[name] = agent
            return agent
        
        return None
    
    @classmethod
    def list_agents(cls) -> List[Dict[str, Any]]:
        """列出所有已注册的 Agent"""
        return [
            {
                "name": name,
                "description": agent_class.description,
                "type": agent_class.agent_type.value,
                "version": agent_class.version,
            }
            for name, agent_class in cls._agents.items()
        ]
    
    @classmethod
    def get_agents_by_type(cls, agent_type: AgentType) -> List[BaseAgent]:
        """根据类型获取 Agent 列表"""
        return [
            cls.get_agent(name)
            for name, agent_class in cls._agents.items()
            if agent_class.agent_type == agent_type
        ]


# 便捷函数
register_agent = AgentRegistry.register
get_agent = AgentRegistry.get_agent
list_agents = AgentRegistry.list_agents
