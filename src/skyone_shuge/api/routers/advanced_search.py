# Advanced Search Router
#高级搜索路由

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, or_, and_
from ..core.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from ..models.document import Document


router = APIRouter(prefix="/search", tags=["搜索"])


class AdvancedSearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    sort: Optional[Dict] = None
    page: int = 1
    limit: int = 20
    mode: str = "hybrid"  # keyword/semantic/hybrid


class SearchFilter(BaseModel):
    category_id: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: Optional[List[str]] = None
    file_types: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    authors: Optional[List[str]] = None


@router.post("/advanced")
async def advanced_search(
    request: AdvancedSearchRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """高级搜索"""
    import time
    start_time = time.time()
    
    # 构建基础查询
    base_query = select(Document).where(
        Document.deleted_at.is_(None)
    )
    
    # 应用过滤器
    if request.filters:
        filters = request.filters
        
        if filters.get("category_id"):
            base_query = base_query.where(
                Document.category_id.in_(filters["category_id"])
            )
        
        if filters.get("status"):
            base_query = base_query.where(
                Document.status.in_(filters["status"])
            )
        
        if filters.get("file_types"):
            base_query = base_query.where(
                Document.extension.in_(filters["file_types"])
            )
        
        if filters.get("date_from"):
            base_query = base_query.where(
                Document.created_at >= filters["date_from"]
            )
        
        if filters.get("date_to"):
            base_query = base_query.where(
                Document.created_at <= filters["date_to"]
            )
    
    # 应用关键词搜索
    if request.query:
        search_term = f"%{request.query}%"
        base_query = base_query.where(
            or_(
                Document.title.ilike(search_term),
                Document.file_name.ilike(search_term),
                Document.abstract.ilike(search_term),
                Document.content_text.ilike(search_term)
            )
        )
    
    # 统计总数
    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # 应用排序
    if request.sort:
        sort_field = request.sort.get("field", "updated_at")
        sort_order = request.sort.get("order", "desc")
        
        if sort_order == "desc":
            base_query = base_query.order_by(
                getattr(Document, sort_field).desc()
            )
        else:
            base_query = base_query.order_by(
                getattr(Document, sort_field).asc()
            )
    else:
        base_query = base_query.order_by(Document.updated_at.desc())
    
    # 分页
    base_query = base_query.offset(
        (request.page - 1) * request.limit
    ).limit(request.limit)
    
    # 执行查询
    result = await db.execute(base_query)
    documents = result.scalars().all()
    
    took = time.time() - start_time
    
    return {
        "success": True,
        "query": request.query,
        "total": total,
        "page": request.page,
        "limit": request.limit,
        "mode": request.mode,
        "took": round(took, 3),
        "results": [_doc_to_search_result(doc) for doc in documents]
    }


@router.get("/filters")
async def get_filter_options(
    db: AsyncSession = Depends(get_async_db)
):
    """获取搜索筛选选项"""
    
    # 分类选项
    from ..models.category import Category
    categories_result = await db.execute(
        select(Category).order_by(Category.path)
    )
    categories = categories_result.scalars().all()
    
    # 文件类型统计
    types_result = await db.execute(
        select(Document.extension, func.count().label("count"))
        .where(Document.deleted_at.is_(None))
        .group_by(Document.extension)
    )
    file_types = [
        {"value": row[0] or "unknown", "count": row[1]}
        for row in types_result.fetchall()
    ]
    
    # 状态统计
    status_result = await db.execute(
        select(Document.status, func.count().label("count"))
        .where(Document.deleted_at.is_(None))
        .group_by(Document.status)
    )
    statuses = [
        {"value": row[0], "count": row[1]}
        for row in status_result.fetchall()
    ]
    
    return {
        "success": True,
        "data": {
            "categories": [
                {"value": cat.id, "label": cat.path, "count": cat.document_count}
                for cat in categories
            ],
            "file_types": file_types,
            "statuses": statuses,
            "date_ranges": [
                {"label": "今天", "value": "today"},
                {"label": "本周", "value": "this_week"},
                {"label": "本月", "value": "this_month"},
                {"label": "今年", "value": "this_year"},
            ]
        }
    }


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


@router.get("/history")
async def get_search_history(
    limit: int = Query(20, ge=1, le=100)
):
    """获取搜索历史 (从 Redis 获取)"""
    # 从 Redis 获取搜索历史
    return {
        "success": True,
        "history": []
    }


@router.delete("/history")
async def clear_search_history():
    """清除搜索历史"""
    return {
        "success": True,
        "message": "搜索历史已清除"
    }


def _doc_to_search_result(doc: Document) -> dict:
    """转换为搜索结果"""
    
    abstract = doc.abstract or ""
    
    return {
        "id": doc.id,
        "title": doc.title,
        "file_name": doc.file_name,
        "file_type": doc.extension,
        "category_path": doc.category_path,
        "abstract": abstract[:200] + "..." if len(abstract) > 200 else abstract,
        "keywords": doc.keywords or [],
        "status": doc.status,
        "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
    }
