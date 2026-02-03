# Document-Tag Association Model
#文档-标签关联模型

from sqlalchemy import Column, String, DateTime, ForeignKey
from ..core.database import Base
from datetime import datetime
import uuid


class DocumentTag(Base):
    """
    文档-标签关联表 (多对多)
    """
    
    __tablename__ = "document_tags"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"))
    tag_id = Column(String(36), ForeignKey("tags.id", ondelete="CASCADE"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<DocumentTag(document_id={self.document_id}, tag_id={self.tag_id})>"
