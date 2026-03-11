"""
天一阁 - 机器学习模型路由
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime

from ...core.database import get_async_db
from ...schemas.ml import (
    ModelListResponse, ModelStatusResponse, EmbeddingGenerateRequest,
    EmbeddingResponse, LLMCompletionRequest, LLMCompletionResponse,
    EmbeddingModelInfo, LLMModelInfo, EmbeddingProvider, LLMProvider
)
from ...ml.embedding import get_embedding_provider
from ...ml.llm import LLMEngine

router = APIRouter(prefix="/models", tags=["大模型服务"])


@router.get("", response_model=ModelListResponse)
async def list_models(
    db: AsyncSession = Depends(get_async_db)
):
    """获取可用的大模型和向量模型列表"""
    # 模拟可用模型列表（可根据配置生成）
    return ModelListResponse(
        success=True,
        embedding_models=[
            EmbeddingModelInfo(
                provider=EmbeddingProvider.ARK,
                model_name="doubao-text-embedding-v3",
                embedding_dim=1536,
                max_tokens=8192,
                description="Doubao Embedding v3"
            )
        ],
        llm_models=[
            LLMModelInfo(
                provider=LLMProvider.ARK,
                model_name="doubao-seed-2.0-code",
                max_context_tokens=128000,
                max_output_tokens=4096,
                supports_vision=False,
                supports_function_calling=True
            )
        ]
    )


@router.get("/status", response_model=ModelStatusResponse)
async def get_model_status(
    db: AsyncSession = Depends(get_async_db)
):
    """检查当前默认模型的状态及连通性"""
    # TODO: 实现真实的模型 ping 检测
    return ModelStatusResponse(
        success=True,
        embedding_model=EmbeddingModelInfo(
            provider=EmbeddingProvider.ARK,
            model_name="doubao-text-embedding-v3",
            embedding_dim=1536,
            max_tokens=8192
        ),
        llm_model=LLMModelInfo(
            provider=LLMProvider.ARK,
            model_name="doubao-seed-2.0-code",
            max_context_tokens=128000,
            max_output_tokens=4096
        ),
        is_healthy=True,
        last_health_check=datetime.now()
    )


@router.post("/embeddings", response_model=EmbeddingResponse)
async def generate_embeddings(
    request: EmbeddingGenerateRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """生成文本嵌入向量"""
    try:
        # TODO: 集成真实的 ml.embedding
        return EmbeddingResponse(
            success=True,
            embeddings=[[0.0]*1536 for _ in request.texts],
            model=request.model or "doubao-text-embedding-v3",
            total_tokens=sum(len(t) // 4 for t in request.texts)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成嵌入失败: {str(e)}")


@router.post("/chat/completions", response_model=LLMCompletionResponse)
async def create_chat_completion(
    request: LLMCompletionRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """调用LLM生成文本"""
    try:
        # TODO: 集成真实的 ml.llm.LLMEngine
        return LLMCompletionResponse(
            success=True,
            completion="这是一个基于模型的测试回复。",
            model=request.model or "doubao-seed-2.0-code",
            usage={"prompt_tokens": 10, "completion_tokens": 12, "total_tokens": 22},
            finish_reason="stop"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM调用失败: {str(e)}")
