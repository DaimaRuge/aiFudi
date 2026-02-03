# User Model
#用户模型

from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base
import uuid


class User(Base):
    """
    用户模型
    
    Attributes:
        id: 唯一标识
        email: 邮箱 (唯一)
        password_hash: 密码哈希
        name: 用户名
        avatar: 头像 URL
        is_active: 是否激活
        is_verified: 是否已验证邮箱
        last_login_at: 最后登录时间
    """
    
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    avatar = Column(String(512))
    bio = Column(Text)  # 个人简介
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)
    
    # 关系
    documents = relationship("Document", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "avatar": self.avatar,
            "bio": self.bio,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
