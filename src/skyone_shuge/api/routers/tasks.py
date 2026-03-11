"""
天一阁 - 异步任务路由
"""

from fastapi import APIRouter, Depends, Query, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
import uuid

from ...core.database import get_async_db
from ...schemas.tasks import (
    TaskCreateRequest, TaskResponse, TaskListResponse, 
    TaskStatsResponse, TaskStatus, TaskType
)

router = APIRouter(prefix="/tasks", tags=["后台任务"])


@router.post("", response_model=TaskResponse)
async def create_task(
    request: TaskCreateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db)
):
    """创建并执行异步后台任务"""
    task_id = str(uuid.uuid4())
    now = datetime.now()
    
    # 模拟任务入库和分配
    task_data = TaskResponse(
        task_id=task_id,
        task_type=request.task_type,
        status=TaskStatus.QUEUED,
        progress=0,
        created_at=now
    )
    
    # TODO: 实际的 Celery/RQ 任务推送
    # background_tasks.add_task(celery_app.send_task, "process_document", kwargs={"task_id": task_id})
    
    return task_data


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """获取单个任务状态"""
    # TODO: 从 Redis 或任务队列表查询
    return TaskResponse(
        task_id=task_id,
        task_type=TaskType.DOCUMENT_INDEX,
        status=TaskStatus.RUNNING,
        progress=45,
        created_at=datetime.now(),
        started_at=datetime.now()
    )


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[TaskStatus] = None,
    task_type: Optional[TaskType] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db)
):
    """查询历史任务列表"""
    # TODO: 根据条件查询
    return TaskListResponse(
        success=True,
        data=[],
        total=0,
        page=page,
        limit=limit
    )


@router.get("/stats/summary", response_model=TaskStatsResponse)
async def get_task_stats(
    db: AsyncSession = Depends(get_async_db)
):
    """获取队列状态和统计"""
    # TODO: 获取队列积压情况和各状态统计
    return TaskStatsResponse(
        success=True,
        data={
            TaskStatus.PENDING: 5,
            TaskStatus.RUNNING: 2,
            TaskStatus.COMPLETED: 120,
            TaskStatus.FAILED: 1
        }
    )
