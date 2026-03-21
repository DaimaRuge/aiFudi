from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from enum import Enum


class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    PARSED = "parsed"
    ERROR = "error"


class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    IMAGE = "image"
    UNKNOWN = "unknown"


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: str
    username: str
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    subscription_tier: str = "free"


class Document(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    title: str
    original_filename: str
    file_size: int
    mime_type: str
    document_type: DocumentType
    storage_path: str
    status: DocumentStatus = DocumentStatus.UPLOADED
    parsed_content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True


class DocumentChunk(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    chunk_index: int
    chunk_text: str
    chunk_embedding: Optional[List[float]] = None
    created_at: datetime = Field(default_factory=datetime.now)


class KnowledgeQuery(BaseModel):
    query: str
    user_id: UUID
    document_ids: Optional[List[UUID]] = None
    limit: int = 10


class KnowledgeResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    total: int
    processing_time: float


class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatSession(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    title: str
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# API请求/响应模型
class UploadDocumentRequest(BaseModel):
    title: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)


class UploadDocumentResponse(BaseModel):
    document_id: UUID
    status: str
    message: str


class SearchRequest(BaseModel):
    query: str
    limit: int = 10


class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[UUID] = None
    document_context: Optional[List[UUID]] = None


class ChatResponse(BaseModel):
    response: str
    session_id: UUID
    sources: Optional[List[Dict[str, Any]]] = None
    processing_time: float