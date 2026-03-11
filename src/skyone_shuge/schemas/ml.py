"""
天一阁 - 机器学习模型相关数据模型
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EmbeddingProvider(str, Enum):
    """嵌入模型提供方"""
    OPENAI = "openai"
    ARK = "ark"
    SENTENCE_TRANSFORMERS = "sentence_transformers"


class EmbeddingModelInfo(BaseModel):
    """嵌入模型信息"""
    provider: EmbeddingProvider
    model_name: str
    embedding_dim: int
    max_tokens: int
    description: Optional[str] = None


class EmbeddingGenerateRequest(BaseModel):
    """生成嵌入请求"""
    texts: List[str] = Field(..., min_items=1, max_items=100)
    model: Optional[str] = None


class EmbeddingResponse(BaseModel):
    """嵌入响应"""
    success: bool = True
    embeddings: List[List[float]]
    model: str
    total_tokens: int


class LLMProvider(str, Enum):
    """LLM提供方"""
    OPENAI = "openai"
    ARK = "ark"
    ANTHROPIC = "anthropic"


class LLMModelInfo(BaseModel):
    """LLM模型信息"""
    provider: LLMProvider
    model_name: str
    max_context_tokens: int
    max_output_tokens: int
    supports_vision: bool = False
    supports_function_calling: bool = False


class LLMCompletionRequest(BaseModel):
    """LLM补全请求"""
    prompt: str = Field(..., min_length=1)
    model: Optional[str] = None
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(1024, ge=1)
    system_prompt: Optional[str] = None


class LLMCompletionResponse(BaseModel):
    """LLM补全响应"""
    success: bool = True
    completion: str
    model: str
    usage: Dict[str, int]
    finish_reason: str


class ModelListResponse(BaseModel):
    """模型列表响应"""
    success: bool = True
    embedding_models: List[EmbeddingModelInfo]
    llm_models: List[LLMModelInfo]


class ModelStatusResponse(BaseModel):
    """模型状态响应"""
    success: bool = True
    embedding_model: EmbeddingModelInfo
    llm_model: LLMModelInfo
    is_healthy: bool
    last_health_check: datetime
