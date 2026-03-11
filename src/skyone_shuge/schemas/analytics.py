"""
天一阁 - 分析统计相关数据模型
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum


class TimeRange(str, Enum):
    """时间范围"""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class AnalyticsMetric(str, Enum):
    """分析指标"""
    DOCUMENTS_ADDED = "documents_added"
    DOCUMENTS_INDEXED = "documents_indexed"
    SEARCHES = "searches"
    RAG_QUERIES = "rag_queries"
    API_REQUESTS = "api_requests"
    STORAGE_USED = "storage_used"


class DailyStats(BaseModel):
    """每日统计"""
    date: date
    documents_added: int = 0
    documents_indexed: int = 0
    searches: int = 0
    rag_queries: int = 0
    api_requests: int = 0
    storage_used_bytes: int = 0


class CategoryStats(BaseModel):
    """分类统计"""
    category_id: str
    category_path: str
    document_count: int
    total_size_bytes: int
    last_updated: datetime


class FileTypeStats(BaseModel):
    """文件类型统计"""
    extension: str
    document_count: int
    total_size_bytes: int
    percentage: float


class SearchStats(BaseModel):
    """搜索统计"""
    total_searches: int
    unique_queries: int
    top_queries: List[Dict[str, Any]]
    avg_response_time_ms: float
    success_rate: float


class RAGStats(BaseModel):
    """RAG统计"""
    total_queries: int
    avg_sources_used: float
    feedback_positive_rate: float
    avg_response_time_ms: float


class StorageStats(BaseModel):
    """存储统计"""
    total_bytes: int
    total_documents: int
    avg_document_size_bytes: float
    largest_document: Optional[Dict[str, Any]] = None


class AnalyticsOverviewResponse(BaseModel):
    """分析概览响应"""
    success: bool = True
    period_start: date
    period_end: date
    daily_stats: List[DailyStats]
    category_stats: List[CategoryStats]
    file_type_stats: List[FileTypeStats]
    search_stats: SearchStats
    rag_stats: RAGStats
    storage_stats: StorageStats


class AnalyticsRequest(BaseModel):
    """分析请求"""
    time_range: TimeRange = TimeRange.WEEK
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    metrics: Optional[List[AnalyticsMetric]] = None
