"""文档 API 路由"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import os
import uuid
from pathlib import Path

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_active_user
from app.models.models import User, Document, DocumentChunk
from app.schemas.schemas import (
    DocumentResponse,
    DocumentDetail,
    MessageResponse
)
from app.services.document_service import document_service
from app.services.ai_service import ai_service
from app.services.knowledge_service import knowledge_service

router = APIRouter(prefix="/api/documents", tags=["文档"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """上传文档"""
    # 检查文件类型
    if not document_service.is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型。允许的类型: {', '.join(document_service.ALLOWED_EXTENSIONS)}"
        )

    # 检查文件大小
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件过大。最大允许: {settings.MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # 保存文件
    file_ext = document_service.get_file_extension(file.filename)
    file_id = str(uuid.uuid4())
    file_name = f"{file_id}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, file_name)

    async with open(file_path, 'wb') as f:
        f.write(content)

    # 解析文档
    try:
        parsed_content = await document_service.parse_document(file_path, file_ext)
    except Exception as e:
        # 如果解析失败，删除文件
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # 创建文档记录
    document = Document(
        user_id=current_user.id,
        title=Path(file.filename).stem,
        original_filename=file.filename,
        file_path=file_path,
        file_size=len(content),
        mime_type=file.content_type,
        content=parsed_content,
        word_count=document_service.count_words(parsed_content),
        page_count=document_service.estimate_page_count(parsed_content),
        is_processed=True
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    # 异步创建文档分块和知识图谱（简化版：同步执行）
    try:
        # 创建分块
        chunks = document_service.split_into_chunks(parsed_content)
        for i, chunk_text in enumerate(chunks):
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=i,
                chunk_text=chunk_text
            )
            db.add(chunk)

        # 生成摘要
        document.summary = ai_service.generate_summary(parsed_content[:2000])

        # 构建知识图谱
        await knowledge_service.build_knowledge_graph(
            db, current_user.id, document.id, parsed_content
        )

        await db.commit()
    except Exception as e:
        print(f"文档处理警告: {e}")

    return DocumentResponse.model_validate(document)


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取文档列表"""
    result = await db.execute(
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    documents = result.scalars().all()
    return [DocumentResponse.model_validate(doc) for doc in documents]


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取文档详情"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    return DocumentDetail.model_validate(document)


@router.delete("/{document_id}", response_model=MessageResponse)
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除文档"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    # 删除文件
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    # 删除数据库记录（级联删除会自动删除相关数据）
    await db.delete(document)
    await db.commit()

    return MessageResponse(message="文档已删除")


@router.get("/{document_id}/content")
async def get_document_content(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取文档原始内容"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    return {
        "content": document.content,
        "word_count": document.word_count,
        "page_count": document.page_count
    }
