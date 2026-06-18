"""Pydantic Schemas"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ============ 用户相关 ============
class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============ 文档相关 ============
class DocumentBase(BaseModel):
    title: str


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: str
    user_id: str
    original_filename: str
    file_size: Optional[int]
    mime_type: Optional[str]
    word_count: int
    page_count: int
    summary: Optional[str]
    is_processed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentDetail(DocumentResponse):
    content: Optional[str]
    metadata: dict


class DocumentChunkResponse(BaseModel):
    id: str
    chunk_index: int
    chunk_text: str

    class Config:
        from_attributes = True


# ============ 知识图谱相关 ============
class KnowledgeNodeBase(BaseModel):
    node_type: str
    name: str
    description: Optional[str] = None


class KnowledgeNodeCreate(KnowledgeNodeBase):
    document_id: Optional[str] = None


class KnowledgeNodeResponse(KnowledgeNodeBase):
    id: str
    document_id: Optional[str]
    user_id: str
    importance: float
    created_at: datetime

    class Config:
        from_attributes = True


class KnowledgeRelationCreate(BaseModel):
    source_id: str
    target_id: str
    relation_type: str
    weight: float = 1.0


class KnowledgeRelationResponse(BaseModel):
    id: str
    source_id: str
    target_id: str
    relation_type: str
    weight: float

    class Config:
        from_attributes = True


class KnowledgeGraphResponse(BaseModel):
    nodes: List[KnowledgeNodeResponse]
    edges: List[KnowledgeRelationResponse]


# ============ 聊天相关 ============
class ChatSessionCreate(BaseModel):
    title: Optional[str] = "新对话"
    document_id: Optional[str] = None


class ChatSessionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    document_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    content: str
    session_id: Optional[str] = None


class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    document_id: Optional[str] = None


class ChatResponse(BaseModel):
    message: ChatMessageResponse
    session_id: str


# ============ 学习路径相关 ============
class LearningPathCreate(BaseModel):
    title: str
    description: Optional[str] = None
    goal: Optional[str] = None
    difficulty: str = "intermediate"


class LearningUnitCreate(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    duration_minutes: int = 30
    difficulty: str = "intermediate"


class LearningUnitResponse(BaseModel):
    id: str
    path_id: str
    title: str
    description: Optional[str]
    content: Optional[str]
    order_index: int
    duration_minutes: int
    difficulty: str
    is_completed: bool
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class LearningPathResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    goal: Optional[str]
    difficulty: str
    status: str
    progress: float
    created_at: datetime
    units: List[LearningUnitResponse] = []

    class Config:
        from_attributes = True


class LearningPathGenerateRequest(BaseModel):
    topic: str
    difficulty: str = "intermediate"
    duration_hours: int = 10
    document_ids: Optional[List[str]] = None


# ============ 通用响应 ============
class MessageResponse(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    detail: str
    success: bool = False
