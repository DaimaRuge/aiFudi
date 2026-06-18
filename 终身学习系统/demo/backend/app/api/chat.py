"""聊天 API 路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import asyncio

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.models import User, ChatSession, ChatMessage, Document, DocumentChunk
from app.schemas.schemas import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatRequest,
    ChatResponse
)
from app.services.ai_service import ai_service

router = APIRouter(prefix="/api/chat", tags=["聊天"])


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    session_data: ChatSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建聊天会话"""
    # 如果指定了文档，验证文档存在
    if session_data.document_id:
        result = await db.execute(
            select(Document).where(
                Document.id == session_data.document_id,
                Document.user_id == current_user.id
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文档不存在"
            )

    session = ChatSession(
        user_id=current_user.id,
        title=session_data.title,
        document_id=session_data.document_id
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return ChatSessionResponse.model_validate(session)


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def list_chat_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取聊天会话列表"""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
    )
    sessions = result.scalars().all()
    return [ChatSessionResponse.model_validate(s) for s in sessions]


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_session_messages(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取会话消息"""
    # 验证会话属于当前用户
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )

    # 获取消息
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    return [ChatMessageResponse.model_validate(m) for m in messages]


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """发送消息并获取 AI 回复"""
    # 获取或创建会话
    if request.session_id:
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == request.session_id,
                ChatSession.user_id == current_user.id
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )
    else:
        # 创建新会话
        session = ChatSession(
            user_id=current_user.id,
            title=request.message[:50] + ("..." if len(request.message) > 50 else ""),
            document_id=request.document_id
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

    # 保存用户消息
    user_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)

    # 获取上下文
    context = await get_chat_context(db, session, request.message)

    # 生成 AI 回复
    if asyncio.iscoroutinefunction(ai_service.generate_response):
        ai_response = await ai_service.generate_response(request.message, context)
    else:
        ai_response = ai_service.generate_response(request.message, context)

    # 保存 AI 消息
    assistant_message = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=ai_response
    )
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)

    return ChatResponse(
        message=ChatMessageResponse.model_validate(assistant_message),
        session_id=session.id
    )


async def get_chat_context(
    db: AsyncSession,
    session: ChatSession,
    query: str
) -> str:
    """获取聊天上下文"""
    context_parts = []

    # 如果会话关联了文档，获取相关内容
    if session.document_id:
        result = await db.execute(
            select(Document).where(Document.id == session.document_id)
        )
        document = result.scalar_one_or_none()

        if document and document.content:
            # 简化版：返回文档的前 2000 字符作为上下文
            context_parts.append(f"【文档：{document.title}】\n{document.content[:2000]}")

    # 获取最近的对话历史
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(5)
    )
    recent_messages = list(reversed(result.scalars().all()))

    if recent_messages:
        history = "\n".join([
            f"{'用户' if m.role == 'user' else '助手'}: {m.content}"
            for m in recent_messages[:-1]  # 排除当前消息
        ])
        if history:
            context_parts.append(f"【对话历史】\n{history}")

    return "\n\n".join(context_parts)


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除聊天会话"""
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )

    await db.delete(session)
    await db.commit()

    return {"message": "会话已删除"}
