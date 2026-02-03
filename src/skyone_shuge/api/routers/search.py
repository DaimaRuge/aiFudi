"""
天一阁 - 搜索路由
"""

from fastapi import APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from typing import Optional
from ..core.database import get_async_db
from ..models import Document
from .schemas import SearchResponse, DocumentResponse
import time

router = APIRouter(prefix="/search", tags=["搜索"])


@router.get("", response_model=SearchResponse)
async def search_documents(
    q: str = Query(..., min_length=1),
    category_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_async_db)
):
    """搜索文档"""
    
    start_time = time.time()
    
    search_term = f"%{q}%"
    
    query = select(Document).where(
        Document.deleted_at.is_(None),
        or_(
            Document.title.ilike(search_term),
            Document.file_name.ilike(search_term),
            Document.abstract.ilike(search_term),
            Document.content_text.ilike(search_term)
        )
    )
    
    if category_id:
        query = query.where(Document.category_id == category_id)
    
    if status:
        query = query.where(Document.status == status)
    
    # 统计
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # 分页
    query = query.offset((page - 1) * limit).limit(limit)
    query = query.order_by(Document.updated_at.desc())
    
    result = await db.execute(query)
    documents = result.scalars().all()
    
    took = time.time() - start_time
    
    return SearchResponse(
        success=True,
        query=q,
        total=total,
        results=[DocumentResponse.model_validate(doc) for doc in documents],
        took=took
    )


@router.get("/suggest")
async def search_suggestions(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_async_db)
):
    """搜索建议"""
    
    search_term = f"%{q}%"
    
    result = await db.execute(
        select(Document.title)
        .where(
            Document.deleted_at.is_(None),
            Document.title.ilike(search_term)
        )
        .limit(limit)
    )
    
    suggestions = list(set([row[0] for row in result.fetchall() if row[0]]))
    
    return {
        "success": True,
        "suggestions": suggestions[:limit]
    }


@router.get("/filters")
async def get_filter_options(db: AsyncSession = Depends(get_async_db)):
    """获取搜索筛选选项"""
    
    # 分类
    from ..models import Category
    cat_result = await db.execute(
        select(Category).order_by(Category.path)
    )
    categories = cat_result.scalars().all()
    
    # 文件类型统计
    type_result = await db.execute(
        select(Document.extension, func.count().label("count"))
        .where(Document.deleted_at.is_(None))
        .group_by(Document.extension)
    )
    file_types = [
        {"value": row[0] or "unknown", "count": row[1]}
        for row in type_result.fetchall()
    ]
    
    return {
        "success": True,
        "data": {
            "categories": [
                {"value": cat.id, "label": cat.path, "count": cat.document_count}
                for cat in categories
            ],
            "file_types": file_types,
            "statuses": [
                {"label": "待分类", "value": "pending"},
                {"label": "已分类", "value": "classified"}
            ]
        }
    }
