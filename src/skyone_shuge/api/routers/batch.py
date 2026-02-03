# Batch Operations Router
#批量操作路由

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..core.database import get_async_db
from ..models.document import Document
from ..models.category import Category


router = APIRouter(prefix="/batch", tags=["批量操作"])


class BatchOperationRequest(BaseModel):
    document_ids: List[str]
    operation: str  # move/classify/tag/delete/rate


class BatchMoveRequest(BaseModel):
    document_ids: List[str]
    category_id: str


class BatchClassifyRequest(BaseModel):
    document_ids: List[str]
    category_id: str
    force: bool = False


class BatchRateRequest(BaseModel):
    document_ids: List[str]
    rating: int  # 1-5


@router.post("/move")
async def batch_move(
    request: BatchMoveRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """批量移动文档到分类"""
    
    result = {
        "succeeded": 0,
        "failed": 0,
        "errors": []
    }
    
    # 验证分类存在
    cat_result = await db.execute(
        select(Category).where(Category.id == request.category_id)
    )
    category = cat_result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 批量更新
    for doc_id in request.document_ids:
        try:
            doc_result = await db.execute(
                select(Document).where(Document.id == doc_id)
            )
            doc = doc_result.scalar_one_or_none()
            
            if doc:
                doc.category_id = request.category_id
                doc.category_path = category.path
                result["succeeded"] += 1
            else:
                result["failed"] += 1
                result["errors"].append({
                    "document_id": doc_id,
                    "error": "文档不存在"
                })
        except Exception as e:
            result["failed"] += 1
            result["errors"].append({
                "document_id": doc_id,
                "error": str(e)
            })
    
    await db.commit()
    
    return result


@router.post("/classify")
async def batch_classify(
    request: BatchClassifyRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """批量分类文档"""
    
    from ..services.classifier import ClassifierService
    
    result = {
        "succeeded": 0,
        "failed": 0,
        "errors": []
    }
    
    classifier = ClassifierService(db)
    
    for doc_id in request.document_ids:
        try:
            doc_result = await db.execute(
                select(Document).where(Document.id == doc_id)
            )
            doc = doc_result.scalar_one_or_none()
            
            if doc:
                classification = await classifier.classify_document(
                    doc,
                    force=request.force
                )
                
                if classification.get("category_id"):
                    cat_result = await db.execute(
                        select(Category).where(
                            Category.path == classification["category_path"]
                        )
                    )
                    category = cat_result.scalar_one_or_none()
                    
                    if category:
                        doc.category_id = category.id
                        doc.category_path = category.path
                        doc.status = "classified"
                
                result["succeeded"] += 1
            else:
                result["failed"] += 1
                result["errors"].append({
                    "document_id": doc_id,
                    "error": "文档不存在"
                })
        except Exception as e:
            result["failed"] += 1
            result["errors"].append({
                "document_id": doc_id,
                "error": str(e)
            })
    
    await db.commit()
    
    return result


@router.post("/rate")
async def batch_rate(
    request: BatchRateRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """批量评分"""
    
    if not 1 <= request.rating <= 5:
        raise HTTPException(status_code=400, detail="评分必须在 1-5 之间")
    
    result = {
        "succeeded": 0,
        "failed": 0,
        "errors": []
    }
    
    for doc_id in request.document_ids:
        try:
            doc_result = await db.execute(
                select(Document).where(Document.id == doc_id)
            )
            doc = doc_result.scalar_one_or_none()
            
            if doc:
                doc.rating = request.rating
                result["succeeded"] += 1
            else:
                result["failed"] += 1
                result["errors"].append({
                    "document_id": doc_id,
                    "error": "文档不存在"
                })
        except Exception as e:
            result["failed"] += 1
            result["errors"].append({
                "document_id": doc_id,
                "error": str(e)
            })
    
    await db.commit()
    
    return result


@router.post("/delete")
async def batch_delete(
    request: BatchOperationRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """批量删除文档"""
    
    result = {
        "succeeded": 0,
        "failed": 0,
        "deleted": 0,
        "errors": []
    }
    
    for doc_id in request.document_ids:
        try:
            doc_result = await db.execute(
                select(Document).where(Document.id == doc_id)
            )
            doc = doc_result.scalar_one_or_none()
            
            if doc:
                doc.deleted_at = datetime.utcnow()
                result["deleted"] += 1
                result["succeeded"] += 1
            else:
                result["failed"] += 1
                result["errors"].append({
                    "document_id": doc_id,
                    "error": "文档不存在"
                })
        except Exception as e:
            result["failed"] += 1
            result["errors"].append({
                "document_id": doc_id,
                "error": str(e)
            })
    
    await db.commit()
    
    return result


@router.post("/restore")
async def batch_restore(
    request: BatchOperationRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """批量恢复已删除文档"""
    
    result = {
        "succeeded": 0,
        "failed": 0,
        "errors": []
    }
    
    for doc_id in request.document_ids:
        try:
            doc_result = await db.execute(
                select(Document).where(Document.id == doc_id)
            )
            doc = doc_result.scalar_one_or_none()
            
            if doc and doc.deleted_at:
                doc.deleted_at = None
                result["succeeded"] += 1
            else:
                result["failed"] += 1
                result["errors"].append({
                    "document_id": doc_id,
                    "error": "文档不存在或未删除"
                })
        except Exception as e:
            result["failed"] += 1
            result["errors"].append({
                "document_id": doc_id,
                "error": str(e)
            })
    
    await db.commit()
    
    return result
