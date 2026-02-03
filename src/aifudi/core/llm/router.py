#!/usr/bin/env python3
"""
Fudi VoiceOS - LLM Router

混合推理层 - 云端大模型 + 端侧小模型智能分发

功能:
- 意图复杂度判断
- 云端/端侧路由
- 上下文管理
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import asyncio


class ModelType(str, Enum):
    """模型类型"""
    CLOUD_LARGE = "cloud_large"      # DeepSeek-V3 / Qwen-Max
    CLOUD_MEDIUM = "cloud_medium"    # 豆包Pro
    EDGE_SMALL = "edge_small"        # Qwen-1.5B-Int4
    EDGE_TINY = "edge_tiny"          # Qwen-0.5B


class Complexity(str, Enum):
    """任务复杂度"""
    SIMPLE = "simple"        # 本地处理 (开关灯)
    MEDIUM = "medium"        # 简单云端
    COMPLEX = "complex"      # 复杂推理


@dataclass
class RoutingDecision:
    """路由决策"""
    complexity: Complexity
    recommended_model: ModelType
    reasoning: str
    confidence: float


class LLMRouter:
    """
    LLM 路由器
    
    智能判断任务复杂度，选择合适的模型
    """
    
    # 复杂度关键词
    SIMPLE_KEYWORDS = [
        "打开", "关闭", "调亮", "调暗", "开关",
        "播放", "暂停", "停止",
        "温度", "模式",
        "查询状态", "现在几"
    ]
    
    COMPLEX_KEYWORDS = [
        "帮我", "能不能", "怎么办",
        "分析", "比较", "推荐",
        "计划", "安排", "搜索",
        "周末", "旅行", "露营"
    ]
    
    def __init__(self):
        self.models: Dict[ModelType, Dict] = {}
        self.cache = {}
    
    def register_model(self, model_type: ModelType, endpoint: str, api_key: str = None):
        """注册模型"""
        self.models[model_type] = {
            "endpoint": endpoint,
            "api_key": api_key,
            "type": model_type
        }
    
    async def route(self, query: str, context: Dict = None) -> RoutingDecision:
        """
        路由决策
        
        Args:
            query: 用户查询
            context: 上下文
            
        Returns:
            RoutingDecision: 路由决策
        """
        
        # 1. 分析复杂度
        complexity = self._analyze_complexity(query)
        
        # 2. 选择模型
        model = self._select_model(complexity)
        
        # 3. 生成决策
        decision = RoutingDecision(
            complexity=complexity,
            recommended_model=model,
            reasoning=self._explain_decision(complexity, query),
            confidence=0.85
        )
        
        return decision
    
    def _analyze_complexity(self, query: str) -> Complexity:
        """分析任务复杂度"""
        query_lower = query.lower()
        
        # 检查简单指令
        simple_score = sum(1 for kw in self.SIMPLE_KEYWORDS if kw in query_lower)
        
        # 检查复杂指令
        complex_score = sum(1 for kw in self.COMPLEX_KEYWORDS if kw in query_lower)
        
        if complex_score > simple_score:
            return Complexity.COMPLEX
        elif simple_score > 0:
            return Complexity.SIMPLE
        else:
            return Complexity.MEDIUM
    
    def _select_model(self, complexity: Complexity) -> ModelType:
        """选择模型"""
        mapping = {
            Complexity.SIMPLE: ModelType.EDGE_SMALL,
            Complexity.MEDIUM: ModelType.CLOUD_MEDIUM,
            Complexity.COMPLEX: ModelType.CLOUD_LARGE
        }
        return mapping.get(complexity, ModelType.CLOUD_MEDIUM)
    
    def _explain_decision(self, complexity: Complexity, query: str) -> str:
        """解释决策"""
        explanations = {
            Complexity.SIMPLE: "检测到简单设备控制指令，可本地处理",
            Complexity.MEDIUM: "检测到一般查询，云端处理",
            Complexity.COMPLEX: "检测到复杂推理任务，需要云端大模型"
        }
        return explanations.get(complexity, "默认路由到云端")
    
    async def call_cloud(self, query: str, model: ModelType = ModelType.CLOUD_LARGE) -> str:
        """
        调用云端模型
        
        TODO: 接入实际 API (DeepSeek / Qwen / 豆包)
        """
        # 模拟响应
        return f"[Cloud {model.value}] 已处理: {query}"
    
    async def call_edge(self, query: str, model: ModelType = ModelType.EDGE_SMALL) -> str:
        """
        调用端侧模型
        
        TODO: 接入本地 LLM (Qwen-1.5B-Int4)
        """
        # 模拟响应
        return f"[Edge {model.value}] 已处理: {query}"


class ContextManager:
    """
    上下文管理器
    
    管理多轮对话状态
    """
    
    def __init__(self, max_history: int = 10):
        self.history: List[Dict] = []
        self.max_history = max_history
    
    async def add(self, role: str, content: str):
        """添加对话"""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": self._timestamp()
        })
        
        # 限制历史长度
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_context(self) -> List[Dict]:
        """获取上下文"""
        return self.history
    
    def clear(self):
        """清空上下文"""
        self.history = []
    
    def _timestamp(self) -> str:
        import datetime
        return datetime.datetime.now().isoformat()
