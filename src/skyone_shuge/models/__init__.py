"""
天一阁 - 数据模型 (v3.0.1)

文档、文件夹、标签、知识图谱等数据模型
"""

from sqlalchemy import (
    Column, String, Text, Integer, DateTime, ForeignKey, 
    Boolean, Index, Table, JSON, Float, ARRAY
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime
import uuid
from ..core.database import Base


# ==================== 关联表 ====================

# 文档-标签关联表
document_tags = Table(
    "document_tags",
    Base.metadata,
    Column("document_id", String(36), ForeignKey("documents.id", ondelete="CASCADE")),
    Column("tag_id", String(36), ForeignKey("tags.id", ondelete="CASCADE"))
)

# 文档-文件夹关联表 (多对多，一个文档可以在多个文件夹)
document_folders = Table(
    "document_folders",
    Base.metadata,
    Column("document_id", String(36), ForeignKey("documents.id", ondelete="CASCADE")),
    Column("folder_id", String(36), ForeignKey("folders.id", ondelete="CASCADE"))
)

# 实体-文档关联表
entity_documents = Table(
    "entity_documents",
    Base.metadata,
    Column("entity_id", String(36), ForeignKey("entities.id", ondelete="CASCADE")),
    Column("document_id", String(36), ForeignKey("documents.id", ondelete="CASCADE"))
)

# 实体-关系关联表
entity_relations = Table(
    "entity_relations",
    Base.metadata,
    Column("source_entity_id", String(36), ForeignKey("entities.id", ondelete="CASCADE")),
    Column("target_entity_id", String(36), ForeignKey("entities.id", ondelete="CASCADE")),
    Column("relation_id", String(36), ForeignKey("relations.id", ondelete="CASCADE"))
)


# ==================== 核心实体 ====================

class Folder(Base):
    """文件夹模型 - 支持虚拟文件夹结构"""
    
    __tablename__ = "folders"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    parent_id = Column(String(36), ForeignKey("folders.id", ondelete="CASCADE"))
    path = Column(String(1024), nullable=False)  # 完整路径，如 /知识库/技术文档/
    
    color = Column(String(7), default="#2196F3")
    icon = Column(String(50))
    description = Column(Text)
    sort_order = Column(Integer, default=0)
    
    is_virtual = Column(Boolean, default=False)  # 是否为虚拟文件夹（智能文件夹）
    filter_rules = Column(JSON)  # 智能文件夹的过滤规则
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)
    
    # 关系
    parent = relationship("Folder", remote_side=[id], backref="children")
    documents = relationship("Document", secondary=document_folders, back_populates="folders")
    
    # 索引
    __table_args__ = (
        Index("idx_folders_parent", "parent_id"),
        Index("idx_folders_path", "path"),
        Index("idx_folders_deleted", "deleted_at"),
    )
    
    def __repr__(self):
        return f"<Folder(id={self.id}, name={self.name}, path={self.path})>"


class Document(Base):
    """文档模型 - 核心实体"""
    
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 文件信息
    file_path = Column(String(2048), nullable=False)
    file_name = Column(String(512), nullable=False)
    file_hash = Column(String(64), unique=True, nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(100))
    extension = Column(String(20))
    mime_type = Column(String(100))
    
    # 元数据 - 自动提取
    title = Column(String(512))
    authors = Column(ARRAY(Text))
    abstract = Column(Text)
    summary = Column(Text)  # AI 生成的摘要
    keywords = Column(ARRAY(Text))
    language = Column(String(10), default="zh")
    content_text = Column(Text)  # 纯文本内容
    content_html = Column(Text)  # HTML 格式化内容
    
    # 元数据 - 自定义
    custom_title = Column(String(512))
    custom_description = Column(Text)
    custom_metadata = Column(JSON)  # 用户自定义的元数据
    
    # 状态
    status = Column(String(20), default="pending")  # pending, processing, indexed, error
    processing_error = Column(Text)
    processing_progress = Column(Integer, default=0)  # 0-100
    
    # 质量评分
    quality_score = Column(Float, default=0.0)  # 0.0-1.0，文档质量评分
    relevance_score = Column(Float, default=0.0)  # 相关性评分
    
    # 索引信息
    indexed_at = Column(DateTime)
    content_hash = Column(String(64))  # 用于检测内容变化
    vector_indexed = Column(Boolean, default=False)
    
    # 同步
    sync_status = Column(String(20), default="synced")
    sync_version = Column(Integer, default=0)
    
    # 访问统计
    view_count = Column(Integer, default=0)
    last_viewed_at = Column(DateTime)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)
    
    # 关系
    folders = relationship("Folder", secondary=document_folders, back_populates="documents")
    tags = relationship("Tag", secondary=document_tags, back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    entities = relationship("Entity", secondary=entity_documents, back_populates="documents")
    
    # 索引
    __table_args__ = (
        Index("idx_documents_status", "status"),
        Index("idx_documents_updated", "updated_at"),
        Index("idx_documents_hash", "file_hash"),
        Index("idx_documents_deleted", "deleted_at"),
        Index("idx_documents_created", "created_at"),
    )
    
    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title or self.file_name})>"


class DocumentChunk(Base):
    """文档分块 - 用于向量检索"""
    
    __tablename__ = "document_chunks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    chunk_index = Column(Integer, nullable=False)  # 分块序号
    content = Column(Text, nullable=False)  # 分块内容
    content_preview = Column(String(500))  # 内容预览
    
    # 位置信息
    start_offset = Column(Integer)  # 在原文中的起始位置
    end_offset = Column(Integer)  # 在原文中的结束位置
    page_number = Column(Integer)  # 页码（PDF等）
    
    # 元数据
    section_title = Column(String(512))  # 所属章节标题
    heading_level = Column(Integer)  # 标题级别（h1, h2, etc.）
    chunk_metadata = Column(JSON)  # 额外的元数据
    
    # 向量信息
    embedding_id = Column(String(255))  # 向量数据库中的ID
    embedding_model = Column(String(100))  # 使用的嵌入模型
    has_embedding = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    document = relationship("Document", back_populates="chunks")
    
    # 索引
    __table_args__ = (
        Index("idx_chunks_document", "document_id"),
        Index("idx_chunks_index", "chunk_index"),
    )
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, doc_id={self.document_id}, index={self.chunk_index})>"


class Tag(Base):
    """标签模型"""
    
    __tablename__ = "tags"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True)  # URL友好的名称
    
    color = Column(String(7), default="#9E9E9E")
    description = Column(Text)
    icon = Column(String(50))
    
    # 分类
    category = Column(String(50))  # 标签分类
    
    usage_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    documents = relationship("Document", secondary=document_tags, back_populates="tags")
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"


# ==================== 知识图谱 ====================

class Entity(Base):
    """知识图谱 - 实体"""
    
    __tablename__ = "entities"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    canonical_name = Column(String(255))  # 标准名称
    
    entity_type = Column(String(50), nullable=False)  # 实体类型：person, organization, location, concept, etc.
    description = Column(Text)
    
    # 属性
    properties = Column(JSON)  # 实体属性
    
    # 来源
    source = Column(String(50))  # 来源：manual, auto-extracted, etc.
    confidence = Column(Float, default=1.0)  # 置信度
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    documents = relationship("Document", secondary=entity_documents, back_populates="entities")
    
    # 索引
    __table_args__ = (
        Index("idx_entities_type", "entity_type"),
        Index("idx_entities_name", "name"),
    )
    
    def __repr__(self):
        return f"<Entity(id={self.id}, name={self.name}, type={self.entity_type})>"


class Relation(Base):
    """知识图谱 - 关系"""
    
    __tablename__ = "relations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    source_entity_id = Column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    target_entity_id = Column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    
    relation_type = Column(String(50), nullable=False)  # 关系类型：works_for, located_in, etc.
    description = Column(Text)
    
    # 属性
    properties = Column(JSON)
    
    # 来源
    source = Column(String(50))
    confidence = Column(Float, default=1.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 索引
    __table_args__ = (
        Index("idx_relations_source", "source_entity_id"),
        Index("idx_relations_target", "target_entity_id"),
        Index("idx_relations_type", "relation_type"),
    )
    
    def __repr__(self):
        return f"<Relation(id={self.id}, type={self.relation_type})>"


# ==================== 其他 ====================

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
    is_admin = Column(Boolean, default=False)
    
    preferences = Column(JSON)  # 用户偏好设置
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class SearchHistory(Base):
    """搜索历史记录"""
    
    __tablename__ = "search_history"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"))
    
    query = Column(Text, nullable=False)
    query_type = Column(String(20), default="text")  # text, semantic, hybrid
    
    result_count = Column(Integer, default=0)
    clicked_document_id = Column(String(36), ForeignKey("documents.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 索引
    __table_args__ = (
        Index("idx_search_user", "user_id"),
        Index("idx_search_created", "created_at"),
    )
