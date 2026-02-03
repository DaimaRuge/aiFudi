"""
天一阁 - 文档路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional
from datetime import datetime
from ..core.database import get_async_db
from ..models import Document, Category
from .schemas import DocumentResponse, DocumentListResponse

router = APIRouter(prefix="/documents", tags=["文档"])


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """获取文档列表"""
    
    query = select(Document).where(Document.deleted_at.is_(None))
    
    if category_id:
        query = query.where(Document.category_id == category_id)
    
    if status:
        query = query.where(Document.status == status)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Document.title.ilike(search_term),
                Document.file_name.ilike(search_term)
            )
        )
    
    # 统计
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # 分页
    query = query.offset((page - 1) * limit).limit(limit)
    query = query.order_by(Document.updated_at.desc())
    
    result = await db.execute(query)
    documents = result.scalars().all()
    
    return DocumentListResponse(
        success=True,
        data=[DocumentResponse.model_validate(doc) for doc in documents],
        total=total,
        page=page,
        limit=limit
    )


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str, db: AsyncSession = Depends(get_async_db)):
    """获取文档详情"""
    
    result = await db.execute(
        select(Document).where(
            Document.id == doc_id,
            Document.deleted_at.is_(None)
        )
    )
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    return DocumentResponse.model_validate(doc)


@router.put("/{doc_id}")
async def update_document(
    doc_id: str,
    updates: dict,
    db: AsyncSession = Depends(get_async_db)
):
    """更新文档"""
    
    result = await db.execute(
        select(Document).where(Document.id == doc_id)
    )
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    for key, value in updates.items():
        if hasattr(doc, key) and key not in ["id", "file_hash", "created_at"]:
            setattr(doc, key, value)
    
    doc.updated_at = datetime.utcnow()
    await db.commit()
    
    return {"success": True, "message": "更新成功"}


@router.delete("/{doc_id}")
async def delete_document(doc_id: str, db: AsyncSession = Depends(get_async_db)):
    """删除文档 (软删除)"""
    
    result = await db.execute(
        select(Document).where(Document.id == doc_id)
    )
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    doc.deleted_at = datetime.utcnow()
    await db.commit()
    
    return {"success": True, "message": "删除成功"}


@router.post("/{doc_id}/classify")
async def classify_document(doc_id: str, force: bool = False, db: AsyncSession = Depends(get_async_db)):
    """AI 分类文档"""
    
    from ..services.classifier import ClassifierService
    
    result = await db.execute(
        select(Document).where(Document.id == doc_id)
    )
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    classifier = ClassifierService(db)
    result = await classifier.classify_document(doc, force=force)
    
    return {"success": True, "data": result}
