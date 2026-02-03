"""
天一阁 - 数据模型

文档、分类、标签等数据模型
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Boolean, Index, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from .database import Base
import uuid


# 文档-标签关联表
document_tags = Table(
    "document_tags",
    Base.metadata,
    Column("document_id", String(36), ForeignKey("documents.id", ondelete="CASCADE")),
    Column("tag_id", String(36), ForeignKey("tags.id", ondelete="CASCADE"))
)


class Document(Base):
    """文档模型"""
    
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_path = Column(String(2048), nullable=False)
    file_name = Column(String(512), nullable=False)
    file_hash = Column(String(64), unique=True, nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(100))
    extension = Column(String(20))
    
    # 元数据
    title = Column(String(512))
    authors = Column(ARRAY(Text))
    abstract = Column(Text)
    keywords = Column(ARRAY(Text))
    language = Column(String(10), default="zh")
    content_text = Column(Text)
    
    # 分类
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"))
    category_path = Column(String(512))
    
    # 状态
    status = Column(String(20), default="pending")
    rating = Column(Integer, default=0)
    
    # 自定义命名
    custom_name = Column(String(512))
    custom_number = Column(String(100))
    
    # 索引信息
    indexed_at = Column(DateTime)
    content_hash = Column(String(64))
    
    # 同步
    sync_status = Column(String(20), default="synced")
    sync_version = Column(Integer, default=0)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)
    
    # 关系
    category = relationship("Category", back_populates="documents")
    tags = relationship("Tag", secondary=document_tags, back_populates="documents")
    
    # 索引
    __table_args__ = (
        Index("idx_documents_category", "category_id"),
        Index("idx_documents_status", "status"),
        Index("idx_documents_updated", "updated_at"),
        Index("idx_documents_hash", "file_hash"),
    )
    
    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title})>"


class Category(Base):
    """分类模型"""
    
    __tablename__ = "categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    parent_id = Column(String(36), ForeignKey("categories.id", ondelete="CASCADE"))
    path = Column(String(512), unique=True, nullable=False)
    
    type = Column(String(20), default="user")  # system/user/project
    description = Column(Text)
    color = Column(String(7), default="#2196F3")
    icon = Column(String(50))
    sort_order = Column(Integer, default=0)
    rules = Column(Text)  # JSON
    
    document_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    parent = relationship("Category", remote_side=[id], backref="children")
    documents = relationship("Document", back_populates="category")
    
    # 索引
    __table_args__ = (
        Index("idx_categories_parent", "parent_id"),
        Index("idx_categories_path", "path"),
    )
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"


class Tag(Base):
    """标签模型"""
    
    __tablename__ = "tags"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    color = Column(String(7), default="#9E9E9E")
    description = Column(Text)
    usage_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    documents = relationship("Document", secondary=document_tags, back_populates="tags")
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"


class User(Base):
    """用户模型"""
    
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    avatar = Column(String(512))
    bio = Column(Text)
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
