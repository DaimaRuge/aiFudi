"""
天一阁 - RAG相关数据模型
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class RAGQueryRequest(BaseModel):
    """RAG查询请求"""
    query: str = Field(..., min_length=1, description="用户查询")
    top_k: int = Field(5, ge=1, le=20, description="返回结果数量")
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0, description="相似度阈值")
    include_raw_chunks: bool = Field(False, description="是否包含原始块")
    stream: bool = Field(False, description="是否流式输出")


class RAGSourceDocument(BaseModel):
    """RAG源文档"""
    document_id: str
    title: Optional[str] = None
    file_name: str
    chunk_id: str
    chunk_index: int
    content: str
    similarity_score: float
    page_number: Optional[int] = None


class RAGAnswer(BaseModel):
    """RAG回答"""
    answer: str
    sources: List[RAGSourceDocument]
    total_sources: int
    took: float
    generated_at: datetime


class RAGResponse(BaseModel):
    """RAG查询响应"""
    success: bool = True
    data: RAGAnswer


class RAGFeedbackRequest(BaseModel):
    """RAG反馈请求"""
    query_id: str
    helpful: bool
    comment: Optional[str] = None


class ChunkInfo(BaseModel):
    """块信息"""
    chunk_id: str
    document_id: str
    chunk_index: int
    content_preview: str
    token_count: int
    created_at: datetime


class DocumentChunksResponse(BaseModel):
    """文档块列表响应"""
    success: bool = True
    data: List[ChunkInfo]
    total: int
