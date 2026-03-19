"""学习路径 API 路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import asyncio

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.models import User, LearningPath, LearningUnit
from app.schemas.schemas import (
    LearningPathCreate,
    LearningPathResponse,
    LearningPathGenerateRequest,
    LearningUnitResponse,
    MessageResponse
)
from app.services.ai_service import ai_service

router = APIRouter(prefix="/api/learning", tags=["学习路径"])


@router.post("/paths", response_model=LearningPathResponse, status_code=status.HTTP_201_CREATED)
async def create_learning_path(
    path_data: LearningPathCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建学习路径"""
    path = LearningPath(
        user_id=current_user.id,
        title=path_data.title,
        description=path_data.description,
        goal=path_data.goal,
        difficulty=path_data.difficulty
    )
    db.add(path)
    await db.commit()
    await db.refresh(path)

    return LearningPathResponse.model_validate(path)


@router.post("/paths/generate", response_model=LearningPathResponse, status_code=status.HTTP_201_CREATED)
async def generate_learning_path(
    request: LearningPathGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """AI 生成学习路径"""
    # 调用 AI 服务生成学习路径
    if asyncio.iscoroutinefunction(ai_service.generate_learning_path):
        path_data = await ai_service.generate_learning_path(
            request.topic, request.difficulty
        )
    else:
        path_data = ai_service.generate_learning_path(
            request.topic, request.difficulty
        )

    # 创建学习路径
    path = LearningPath(
        user_id=current_user.id,
        title=path_data.get("title", f"{request.topic} 学习路径"),
        description=path_data.get("description", ""),
        goal=path_data.get("goal", request.topic),
        difficulty=path_data.get("difficulty", request.difficulty)
    )
    db.add(path)
    await db.flush()  # 获取 path.id

    # 创建学习单元
    units_data = path_data.get("units", [])
    for i, unit_data in enumerate(units_data):
        unit = LearningUnit(
            path_id=path.id,
            title=unit_data.get("title", f"单元 {i+1}"),
            description=unit_data.get("description", ""),
            content=unit_data.get("content", ""),
            order_index=i,
            duration_minutes=unit_data.get("duration_minutes", 30),
            difficulty=unit_data.get("difficulty", request.difficulty)
        )
        db.add(unit)

    await db.commit()
    await db.refresh(path)

    # 重新查询以获取完整数据
    result = await db.execute(
        select(LearningPath)
        .where(LearningPath.id == path.id)
    )
    path = result.scalar_one()

    return LearningPathResponse.model_validate(path)


@router.get("/paths", response_model=List[LearningPathResponse])
async def list_learning_paths(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取学习路径列表"""
    result = await db.execute(
        select(LearningPath)
        .where(LearningPath.user_id == current_user.id)
        .order_by(LearningPath.created_at.desc())
    )
    paths = result.scalars().all()
    return [LearningPathResponse.model_validate(p) for p in paths]


@router.get("/paths/{path_id}", response_model=LearningPathResponse)
async def get_learning_path(
    path_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取学习路径详情"""
    result = await db.execute(
        select(LearningPath).where(
            LearningPath.id == path_id,
            LearningPath.user_id == current_user.id
        )
    )
    path = result.scalar_one_or_none()

    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习路径不存在"
        )

    return LearningPathResponse.model_validate(path)


@router.put("/paths/{path_id}/units/{unit_id}/complete", response_model=MessageResponse)
async def complete_learning_unit(
    path_id: str,
    unit_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """完成学习单元"""
    # 验证学习路径
    result = await db.execute(
        select(LearningPath).where(
            LearningPath.id == path_id,
            LearningPath.user_id == current_user.id
        )
    )
    path = result.scalar_one_or_none()

    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习路径不存在"
        )

    # 查找学习单元
    result = await db.execute(
        select(LearningUnit).where(
            LearningUnit.id == unit_id,
            LearningUnit.path_id == path_id
        )
    )
    unit = result.scalar_one_or_none()

    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习单元不存在"
        )

    # 标记完成
    from datetime import datetime
    unit.is_completed = True
    unit.completed_at = datetime.utcnow()

    # 更新学习路径进度
    result = await db.execute(
        select(LearningUnit).where(LearningUnit.path_id == path_id)
    )
    all_units = result.scalars().all()
    completed_count = sum(1 for u in all_units if u.is_completed)
    path.progress = completed_count / len(all_units) if all_units else 0

    if path.progress >= 1.0:
        path.status = "completed"

    await db.commit()

    return MessageResponse(
        message=f"已完成学习单元：{unit.title}",
        success=True
    )


@router.delete("/paths/{path_id}", response_model=MessageResponse)
async def delete_learning_path(
    path_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除学习路径"""
    result = await db.execute(
        select(LearningPath).where(
            LearningPath.id == path_id,
            LearningPath.user_id == current_user.id
        )
    )
    path = result.scalar_one_or_none()

    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习路径不存在"
        )

    await db.delete(path)
    await db.commit()

    return MessageResponse(message="学习路径已删除")
