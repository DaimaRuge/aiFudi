# Tag Model
#标签模型

from sqlalchemy import Column, String, Integer, DateTime, Text
from datetime import datetime
from ..core.database import Base
import uuid


class Tag(Base):
    """
    标签模型
    
    Attributes:
        id: 唯一标识
        name: 标签名称 (唯一)
        color: 标签颜色
        description: 描述
        usage_count: 使用次数
    """
    
    __tablename__ = "tags"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    color = Column(String(7), default="#9E9E9E")
    description = Column(Text)
    usage_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"
