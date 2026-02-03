# LLM Provider - OpenAI
#大语言模型集成 - OpenAI

from typing import Dict, List, Any, Optional
from ..core.config import settings
import json


class OpenAILLM:
    """
    OpenAI LLM 集成
    
    支持 GPT-4, GPT-4-Turbo, GPT-3.5-Turbo
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.base_url = "https://api.openai.com/v1"
    
    async def complete(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> str:
        """
        文本补全
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度 (0-1)
            max_tokens: 最大 token 数
            
        Returns:
            str: 生成的文本
        """
        
        import openai
        
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            client = openai.AsyncOpenAI(api_key=self.api_key)
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI API 错误: {e}")
            raise
    
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """
        文本向量化
        
        Args:
            texts: 文本列表
            
        Returns:
            List[List[float]]: 向量列表
        """
        
        import openai
        
        try:
            client = openai.AsyncOpenAI(api_key=self.api_key)
            
            response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            
            return [data.embedding for data in response.data]
            
        except Exception as e:
            print(f"OpenAI Embedding API 错误: {e}")
            raise


class AnthropicLLM:
    """
    Anthropic Claude LLM 集成
    
    支持 Claude 3 Opus, Sonnet, Haiku
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or settings.ANTHROPIC_MODEL
        self.base_url = "https://api.anthropic.com/v1"
    
    async def complete(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> str:
        """Claude 文本补全"""
        
        import anthropic
        
        messages = []
        
        if system_prompt:
            messages.append({"role": "user", "content": f"\n\nHuman: {system_prompt}\n\n{prompt}"})
        else:
            messages.append({"role": "user", "content": prompt})
        
        try:
            client = anthropic.AsyncAnthropic(api_key=self.api_key)
            
            response = await client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"Anthropic API 错误: {e}")
            raise
    
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Anthropic 目前不支持 embedding，使用 OpenAI"""
        
        # 降级到 OpenAI
        openai = OpenAILLM()
        return await openai.embed(texts)


class LLMRouter:
    """
    LLM 路由器
    
    根据任务类型自动选择最佳模型
    """
    
    ROUTING = {
        "classification": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.3
        },
        "extraction": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.1
        },
        "reasoning": {
            "provider": "anthropic",
            "model": "claude-3-opus-20240229",
            "temperature": 0.7
        },
        "generation": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.8
        },
        "summarization": {
            "provider": "anthropic",
            "model": "claude-3-sonnet-20240229",
            "temperature": 0.5
        },
        "code": {
            "provider": "anthropic",
            "model": "claude-3-opus-20240229",
            "temperature": 0.2
        }
    }
    
    def __init__(self):
        self.providers = {
            "openai": OpenAILLM(),
            "anthropic": AnthropicLLM()
        }
    
    async def complete(
        self,
        task_type: str,
        prompt: str,
        system_prompt: str = None
    ) -> str:
        """
        路由并执行 LLM 任务
        
        Args:
            task_type: 任务类型
            prompt: 提示词
            system_prompt: 系统提示词
            
        Returns:
            str: 生成的文本
        """
        
        config = self.ROUTING.get(task_type, self.ROUTING["generation"])
        
        provider = self.providers.get(config["provider"])
        
        if not provider:
            # 降级到 OpenAI
            provider = self.providers["openai"]
        
        return await provider.complete(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=config.get("temperature", 0.7)
        )
    
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """获取文本向量"""
        
        # 默认使用 OpenAI
        return await self.providers["openai"].embed(texts)


# 便捷函数
def get_llm_router() -> LLMRouter:
    """获取 LLM 路由器实例"""
    return LLMRouter()
