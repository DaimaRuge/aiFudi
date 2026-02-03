# Category Model
#分类模型

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base
import uuid


class Category(Base):
    """
    分类模型
    
    Attributes:
        id: 唯一标识
        name: 分类名称
        parent_id: 父分类 ID
        path: 分类路径 (如 /计算机科学/AI)
        type: 类型 (system/user/project)
        description: 描述
        color: UI 显示颜色
        icon: 图标
        sort_order: 排序
        rules: 自动分类规则 (JSON)
    """
    
    __tablename__ = "categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    parent_id = Column(String(36), ForeignKey("categories.id", ondelete="CASCADE"))
    path = Column(String(512), unique=True, nullable=False)
    
    type = Column(String(20), default="user")  # system/user/project
    description = Column(Text)
    color = Column(String(7), default="#2196F3")  # 十六进制颜色
    icon = Column(String(50))
    sort_order = Column(Integer, default=0)
    rules = Column(Text)  # JSON 格式的自动分类规则
    
    document_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    parent = relationship("Category", remote_side=[id], backref="children")
    documents = relationship("Document", back_populates="category")
    
    # 索引
    __table_args__ = (
        Index("idx_categories_parent", "parent_id"),
        Index("idx_categories_type", "type"),
        Index("idx_categories_path", "path"),
    )
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, path={self.path})>"
    
    @property
    def full_path(self) -> str:
        """完整路径"""
        return self.path
    
    @property
    def level(self) -> int:
        """分类层级"""
        return self.path.count("/")
