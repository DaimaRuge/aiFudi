#!/usr/bin/env python3
"""
Fudi VoiceOS - LLM 引擎

大语言模型引擎

支持:
- 多模型后端 (DeepSeek / Qwen / 豆包)
- 流式输出
- Function Calling
- 提示词工程
"""

import asyncio
from typing import AsyncIterator, Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
import json


class LLMBackend(Enum):
    """LLM 后端"""
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    DOUBAO = "doubao"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class LLMConfig:
    """LLM 配置"""
    backend: LLMBackend = LLMBackend.DEEPSEEK
    model: str = "deepseek-chat"
    api_key: str = ""
    base_url: str = ""
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    enable_stream: bool = True


@dataclass
class Message:
    """消息"""
    role: str  # system/user/assistant/tool
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None


@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str
    tool_calls: List[Dict] = None
    usage: Dict = None
    finish_reason: str = "stop"


class BaseLLMEngine(ABC):
    """LLM 引擎基类"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
    
    @abstractmethod
    async def chat(self, messages: List[Message]) -> LLMResponse:
        """对话"""
        pass
    
    @abstractmethod
    async def stream_chat(self, messages: List[Message]) -> AsyncIterator[str]:
        """流式对话"""
        pass
    
    @abstractmethod
    async def function_call(
        self,
        messages: List[Message],
        tools: List[Dict]
    ) -> LLMResponse:
        """函数调用"""
        pass


class DeepSeekEngine(BaseLLMEngine):
    """
    DeepSeek LLM 引擎
    
    高性价比推理
    """
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = config.base_url or "https://api.deepseek.com"
    
    async def chat(self, messages: List[Message]) -> LLMResponse:
        """对话"""
        # TODO: 调用 DeepSeek API
        print(f"DeepSeek chatting with {len(messages)} messages")
        
        return LLMResponse(
            content="这是 DeepSeek 的回复",
            usage={"prompt_tokens": 100, "completion_tokens": 50}
        )
    
    async def stream_chat(self, messages: List[Message]) -> AsyncIterator[str]:
        """流式对话"""
        # TODO: 实现流式输出
        content = "这是流式回复"
        for char in content:
            yield char
            await asyncio.sleep(0.01)
    
    async def function_call(
        self,
        messages: List[Message],
        tools: List[Dict]
    ) -> LLMResponse:
        """函数调用"""
        print(f"DeepSeek function calling with {len(tools)} tools")
        
        return LLMResponse(
            content="",
            tool_calls=[
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "smart_home_control",
                        "arguments": '{"action": "turn_on", "target": "light"}'
                    }
                }
            ]
        )


class QwenEngine(BaseLLMEngine):
    """
    Qwen LLM 引擎
    
    强逻辑能力，中文理解好
    """
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = config.base_url or "https://dashscope.aliyuncs.com"
    
    async def chat(self, messages: List[Message]) -> LLMResponse:
        """对话"""
        print(f"Qwen chatting with {len(messages)} messages")
        
        return LLMResponse(
            content="这是 Qwen 的回复"
        )
    
    async def stream_chat(self, messages: List[Message]) -> AsyncIterator[str]:
        """流式对话"""
        content = "这是 Qwen 流式回复"
        for char in content:
            yield char
            await asyncio.sleep(0.01)
    
    async def function_call(self, messages: List[Message], tools: List[Dict]) -> LLMResponse:
        """函数调用"""
        return LLMResponse(
            content="",
            tool_calls=[]
        )


class DoubaoEngine(BaseLLMEngine):
    """
    豆包 LLM 引擎
    
    一体化语音方案
    """
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_key = config.api_key
    
    async def chat(self, messages: List[Message]) -> LLMResponse:
        """对话"""
        print("Doubao chatting...")
        
        return LLMResponse(content="这是豆包的回复")
    
    async def stream_chat(self, messages: List[Message]) -> AsyncIterator[str]:
        """流式对话"""
        content = "豆包流式回复"
        for char in content:
            yield char
    
    async def function_call(self, messages: List[Message], tools: List[Dict]) -> LLMResponse:
        """函数调用"""
        return LLMResponse(content="", tool_calls=[])


class PromptEngine:
    """
    提示词引擎
    
    构建高质量提示词
    """
    
    # 系统提示词模板
    SYSTEM_PROMPT = """你是 Fudi，一个智能语音助手。

你的特点:
- 回复简洁、口语化
- 理解用户真实意图
- 主动提供帮助
- 当需要执行操作时，使用 JSON Action 格式

你的工作流程:
1. 理解用户输入
2. 分析意图和参数
3. 如果需要执行操作，输出 JSON Action
4. 否则直接回复

示例:
用户: "打开客厅灯"
输出: {{"action": "smart_home_control", "params": {{"action": "turn_on", "target": "客厅灯"}}}}

用户: "今天天气怎么样"
输出: {{"action": "weather_query", "params": {{"location": "当前城市"}}}}
"""
    
    @staticmethod
    def build_system_prompt(voice: str = "Fudi") -> str:
        """构建系统提示词"""
        return PromptEngine.SYSTEM_PROMPT.replace("Fudi", voice)
    
    @staticmethod
    def build_few_shot_examples() -> List[Dict]:
        """构建少样本示例"""
        return [
            {
                "role": "user",
                "content": "把灯关了"
            },
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "1",
                        "type": "function",
                        "function": {
                            "name": "smart_home_control",
                            "arguments": '{"action": "turn_off", "target": "灯"}'
                        }
                    }
                ]
            }
        ]
    
    @staticmethod
    def format_messages(
        system_prompt: str,
        conversation: List[Dict],
        context: Dict = None
    ) -> List[Message]:
        """格式化消息"""
        messages = [Message(role="system", content=system_prompt)]
        
        for msg in conversation:
            messages.append(Message(
                role=msg["role"],
                content=msg["content"]
            ))
        
        return messages


class LLMManager:
    """
    LLM 管理器
    
    多模型路由和负载均衡
    """
    
    def __init__(self):
        self.engines: Dict[LLMBackend, BaseLLMEngine] = {}
        self.default_engine = LLMBackend.DEEPSEEK
    
    def register_engine(self, backend: LLMBackend, engine: BaseLLMEngine):
        """注册引擎"""
        self.engines[backend] = engine
    
    async def chat(
        self,
        messages: List[Message],
        backend: LLMBackend = None,
        stream: bool = False
    ) -> LLMResponse:
        """对话"""
        engine = self.engines.get(backend or self.default_engine)
        
        if not engine:
            raise ValueError(f"No engine registered for {backend}")
        
        if stream:
            # 流式输出需要特殊处理
            return engine.chat(messages)
        
        return await engine.chat(messages)
    
    async def function_call(
        self,
        messages: List[Message],
        tools: List[Dict],
        backend: LLMBackend = None
    ) -> LLMResponse:
        """函数调用"""
        engine = self.engines.get(backend or self.default_engine)
        
        if not engine:
            raise ValueError(f"No engine registered for {backend}")
        
        return await engine.function_call(messages, tools)


# LLM 工厂
class LLMFactory:
    """LLM 工厂"""
    
    @staticmethod
    def create(config: LLMConfig) -> BaseLLMEngine:
        """创建 LLM 引擎"""
        engines = {
            LLMBackend.DEEPSEEK: DeepSeekEngine,
            LLMBackend.QWEN: QwenEngine,
            LLMBackend.DOUBAO: DoubaoEngine,
        }
        
        engine_class = engines.get(config.backend)
        if engine_class:
            return engine_class(config)
        
        raise ValueError(f"Unknown LLM backend: {config.backend}")


# 测试
async def main():
    """测试 LLM"""
    
    print("=" * 50)
    print("LLM Engine Test")
    print("=" * 50)
    
    # 创建 LLM
    config = LLMConfig(
        backend=LLMBackend.DEEPSEEK,
        model="deepseek-chat"
    )
    
    llm = LLMFactory.create(config)
    
    # 构建消息
    messages = [
        Message(role="user", content="打开客厅灯")
    ]
    
    # 对话
    response = await llm.chat(messages)
    
    print(f"\nResult:")
    print(f"  Content: {response.content}")
    print(f"  Tool Calls: {response.tool_calls}")


if __name__ == "__main__":
    asyncio.run(main())
