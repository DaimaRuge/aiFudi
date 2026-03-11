"""
天一阁 - 搜索相关 schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SearchType(str, Enum):
    """搜索类型"""
    VECTOR = "vector"
    KEYWORD = "keyword"
    HYBRID = "hybrid"


class SearchFilter(BaseModel):
    """搜索过滤器"""
    document_ids: Optional[List[str]] = Field(None, description="文档 ID 列表")
    category_ids: Optional[List[int]] = Field(None, description="分类 ID 列表")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    created_after: Optional[datetime] = Field(None, description="创建时间之后")
    created_before: Optional[datetime] = Field(None, description="创建时间之前")
    file_types: Optional[List[str]] = Field(None, description="文件类型列表")


class SearchQuery(BaseModel):
    """搜索查询"""
    query: str = Field(..., description="搜索查询文本", min_length=1)
    search_type: SearchType = Field(SearchType.HYBRID, description="搜索类型")
    filters: Optional[SearchFilter] = Field(None, description="搜索过滤器")
    enable_rerank: bool = Field(True, description="是否启用重排序")
    page: int = Field(1, description="页码", ge=1)
    page_size: int = Field(20, description="每页数量", ge=1, le=100)


class SearchResult(BaseModel):
    """搜索结果"""
    id: str = Field(..., description="结果 ID")
    title: str = Field(..., description="标题")
    snippet: str = Field(..., description="摘要")
    score: float = Field(..., description="相关性分数")
    search_type: str = Field(..., description="搜索类型")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class SearchResponse(BaseModel):
    """搜索响应"""
    results: List[SearchResult] = Field(..., description="搜索结果列表")
    total: int = Field(..., description="总结果数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    query: str = Field(..., description="原始查询")
    search_time_ms: float = Field(..., description="搜索耗时（毫秒）")


class RAGQuery(BaseModel):
    """RAG 查询"""
    question: str = Field(..., description="用户问题", min_length=1)
    document_ids: Optional[List[str]] = Field(None, description="限定文档 ID 列表")
    category_ids: Optional[List[int]] = Field(None, description="限定分类 ID 列表")
    tags: Optional[List[str]] = Field(None, description="限定标签列表")
    stream: bool = Field(False, description="是否流式输出")


class RAGSource(BaseModel):
    """RAG 来源文档"""
    id: str = Field(..., description="文档 ID")
    title: str = Field(..., description="文档标题")
    content: str = Field(..., description="相关内容片段")
    score: float = Field(..., description="相关性分数")
    page_number: Optional[int] = Field(None, description="页码")


class RAGResponse(BaseModel):
    """RAG 响应"""
    answer: str = Field(..., description="AI 生成的答案")
    sources: List[RAGSource] = Field(..., description="来源文档列表")
    confidence: float = Field(..., description="置信度")
    reasoning: Optional[str] = Field(None, description="推理过程")


class DocumentSuggestion(BaseModel):
    """文档建议"""
    id: str = Field(..., description="文档 ID")
    title: str = Field(..., description="文档标题")
    reason: str = Field(..., description="推荐理由")
    score: float = Field(..., description="推荐分数")


class RelatedDocumentsResponse(BaseModel):
    """相关文档响应"""
    document_id: str = Field(..., description="源文档 ID")
    related_documents: List[DocumentSuggestion] = Field(..., description="相关文档列表")
