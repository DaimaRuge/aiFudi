"""
天一阁 - 异步任务相关数据模型
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """任务类型"""
    DOCUMENT_INDEX = "document_index"
    DOCUMENT_REINDEX = "document_reindex"
    DOCUMENT_DELETE = "document_delete"
    BATCH_INDEX = "batch_index"
    BATCH_REINDEX = "batch_reindex"
    CATEGORY_SYNC = "category_sync"
    EMBEDDING_UPDATE = "embedding_update"
    ANALYTICS_AGGREGATE = "analytics_aggregate"


class TaskCreateRequest(BaseModel):
    """创建任务请求"""
    task_type: TaskType
    document_ids: Optional[List[str]] = None
    category_id: Optional[str] = None
    priority: int = Field(5, ge=1, le=10, description="优先级，1-10")
    metadata: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str
    task_type: TaskType
    status: TaskStatus
    progress: int = Field(0, ge=0, le=100)
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


class TaskListResponse(BaseModel):
    """任务列表响应"""
    success: bool = True
    data: List[TaskResponse]
    total: int
    page: int
    limit: int


class TaskStatsResponse(BaseModel):
    """任务统计响应"""
    success: bool = True
    data: Dict[TaskStatus, int]
