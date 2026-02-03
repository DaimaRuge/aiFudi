# Document Model
#文档模型

from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from ..core.database import Base
import uuid


class Document(Base):
    """
    文档主模型
    
    Attributes:
        id: 唯一标识 (UUID)
        file_path: 文件路径
        file_name: 文件名
        file_hash: 文件哈希 (SHA-256)
        file_size: 文件大小 (字节)
        file_type: MIME 类型
        extension: 文件扩展名
        
        # 元数据
        title: 标题
        subtitle: 副标题
        authors: 作者列表
        abstract: 摘要
        keywords: 关键词列表
        
        # 分类
        category_id: 分类 ID
        category_path: 分类路径
        
        # 状态
        status: 状态 (pending/classified/archived)
        rating: 星级评分 (1-5)
        
        # 自定义命名 (LibIndex 核心功能)
        custom_name: 自定义名称
        custom_number: 自定义编号
        
        # 索引信息
        indexed_at: 索引时间
        content_hash: 内容哈希
        
        # 同步信息
        sync_status: 同步状态
        sync_version: 同步版本
    """
    
    __tablename__ = "documents"
    
    # 核心标识
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 文件信息
    file_path = Column(String(2048), nullable=False)
    file_name = Column(String(512), nullable=False)
    file_hash = Column(String(64), unique=True, nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(100))
    extension = Column(String(20))
    
    # 元数据
    title = Column(String(512))
    subtitle = Column(String(512))
    authors = Column(ARRAY(Text))
    abstract = Column(Text)
    keywords = Column(ARRAY(Text))
    language = Column(String(10), default="zh")
    content_text = Column(Text)  # 纯文本内容
    
    # 分类
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"))
    category_path = Column(String(512))
    
    # 状态
    status = Column(String(20), default="pending")  # pending/classified/archived
    rating = Column(Integer, default=0)
    
    # 自定义命名
    custom_name = Column(String(512))
    custom_number = Column(String(100))
    
    # 索引信息
    indexed_at = Column(DateTime)
    content_hash = Column(String(64))
    has_vector = Column(Boolean, default=False)
    
    # 同步信息
    sync_status = Column(String(20), default="synced")  # synced/pending/error
    sync_version = Column(Integer, default=0)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)
    
    # 关系
    category = relationship("Category", back_populates="documents")
    tags = relationship("Tag", secondary="document_tags", back_populates="documents")
    
    # 索引
    __table_args__ = (
        Index("idx_documents_category", "category_id"),
        Index("idx_documents_status", "status"),
        Index("idx_documents_updated", "updated_at"),
        Index("idx_documents_hash", "file_hash"),
        Index("idx_documents_type", "extension"),
    )
    
    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title}, file_name={self.file_name})>"
    
    @property
    def is_indexed(self) -> bool:
        """是否已索引"""
        return self.indexed_at is not None
    
    @property
    def has_ai_classified(self) -> bool:
        """是否已 AI 分类"""
        return self.category_id is not None and self.status == "classified"
