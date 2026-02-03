"""
天一阁 - Pydantic Schemas

请求/响应数据模型
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DocumentResponse(BaseModel):
    """文档响应"""
    id: str
    title: Optional[str] = None
    file_name: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    extension: Optional[str] = None
    authors: List[str] = []
    category_id: Optional[str] = None
    category_path: Optional[str] = None
    status: str = "pending"
    rating: int = 0
    indexed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """文档列表响应"""
    success: bool
    data: List[DocumentResponse]
    total: int
    page: int
    limit: int


class CategoryResponse(BaseModel):
    """分类响应"""
    id: str
    name: str
    parent_id: Optional[str] = None
    path: str
    type: str = "user"
    color: str = "#2196F3"
    document_count: int = 0
    level: int = 0
    children: List["CategoryResponse"] = []
    
    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    """创建分类请求"""
    name: str
    parent_id: Optional[str] = None
    type: str = "user"
    color: Optional[str] = "#2196F3"


class SearchResponse(BaseModel):
    """搜索响应"""
    success: bool
    query: str
    total: int
    results: List[DocumentResponse]
    took: float = 0.0


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "healthy"
    version: str
    name: str
    database: str = "connected"


class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900


class LoginRequest(BaseModel):
    """登录请求"""
    email: str
    password: str


class RegisterRequest(BaseModel):
    """注册请求"""
    email: str
    password: str
    name: str
