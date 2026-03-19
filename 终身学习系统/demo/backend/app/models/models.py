"""数据库模型"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    learning_paths = relationship("LearningPath", back_populates="user", cascade="all, delete-orphan")


class Document(Base):
    """文档模型"""
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    content = Column(Text)  # 解析后的文本内容
    summary = Column(Text)  # AI 生成的摘要
    word_count = Column(Integer, default=0)
    page_count = Column(Integer, default=0)
    language = Column(String(10), default="zh")
    metadata = Column(JSON, default={})
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    knowledge_nodes = relationship("KnowledgeNode", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """文档分块模型（用于向量检索）"""
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    # 简化版：存储向量索引，实际向量存储在内存中
    embedding_stored = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    document = relationship("Document", back_populates="chunks")


class KnowledgeNode(Base):
    """知识图谱节点"""
    __tablename__ = "knowledge_nodes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    node_type = Column(String(50), nullable=False)  # concept, entity, topic
    name = Column(String(500), nullable=False)
    description = Column(Text)
    importance = Column(Float, default=0.5)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    document = relationship("Document", back_populates="knowledge_nodes")
    outgoing_relations = relationship(
        "KnowledgeRelation",
        foreign_keys="KnowledgeRelation.source_id",
        back_populates="source"
    )
    incoming_relations = relationship(
        "KnowledgeRelation",
        foreign_keys="KnowledgeRelation.target_id",
        back_populates="target"
    )


class KnowledgeRelation(Base):
    """知识图谱关系"""
    __tablename__ = "knowledge_relations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_id = Column(String(36), ForeignKey("knowledge_nodes.id"), nullable=False)
    target_id = Column(String(36), ForeignKey("knowledge_nodes.id"), nullable=False)
    relation_type = Column(String(100), nullable=False)  # relates_to, prerequisite_of, part_of
    weight = Column(Float, default=1.0)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    source = relationship("KnowledgeNode", foreign_keys=[source_id], back_populates="outgoing_relations")
    target = relationship("KnowledgeNode", foreign_keys=[target_id], back_populates="incoming_relations")


class ChatSession(Base):
    """聊天会话"""
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(500), default="新对话")
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=True)  # 关联的文档
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """聊天消息"""
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    session = relationship("ChatSession", back_populates="messages")


class LearningPath(Base):
    """学习路径"""
    __tablename__ = "learning_paths"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    goal = Column(String(500))  # 学习目标
    difficulty = Column(String(20), default="intermediate")  # beginner, intermediate, advanced
    status = Column(String(20), default="active")  # active, completed, paused
    progress = Column(Float, default=0.0)  # 0.0 - 1.0
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="learning_paths")
    units = relationship("LearningUnit", back_populates="path", cascade="all, delete-orphan")


class LearningUnit(Base):
    """学习单元"""
    __tablename__ = "learning_units"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    path_id = Column(String(36), ForeignKey("learning_paths.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    content = Column(Text)  # 学习内容
    order_index = Column(Integer, default=0)
    duration_minutes = Column(Integer, default=30)
    difficulty = Column(String(20), default="intermediate")
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    path = relationship("LearningPath", back_populates="units")
