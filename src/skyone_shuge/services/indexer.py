# Indexer Service
#索引管理服务

from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..models.document import Document
from sqlalchemy.orm import selectinload


class IndexerService:
    """
    索引管理服务
    
    负责文档的增删改查、索引维护、搜索
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, doc_id: str) -> Optional[Document]:
        """根据 ID 获取文档"""
        
        result = await self.db.execute(
            select(Document)
            .options(selectinload(Document.category))
            .where(
                Document.id == doc_id,
                Document.deleted_at.is_(None)
            )
        )
        
        return result.scalar_one_or_none()
    
    async def list_documents(
        self,
        page: int = 1,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """
        获取文档列表
        
        Args:
            page: 页码
            limit: 每页数量
            filters: 筛选条件
            
        Returns:
            Dict: 包含列表和分页信息
        """
        
        query = select(Document).where(Document.deleted_at.is_(None))
        
        if filters:
            if filters.get("category_id"):
                query = query.where(Document.category_id == filters["category_id"])
            
            if filters.get("status"):
                query = query.where(Document.status == filters["status"])
            
            if filters.get("extension"):
                query = query.where(Document.extension == filters["extension"])
        
        # 统计总数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar()
        
        # 分页
        query = query.offset((page - 1) * limit).limit(limit)
        query = query.order_by(Document.updated_at.desc())
        
        result = await self.execute(query)
        documents = result.scalars().all()
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "documents": documents
        }
    
    async def update(
        self,
        doc_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """更新文档"""
        
        result = await self.db.execute(
            select(Document).where(Document.id == doc_id)
        )
        doc = result.scalar_one_or_none()
        
        if not doc:
            return False
        
        # 更新字段
        for key, value in updates.items():
            if hasattr(doc, key) and key not in ["id", "file_hash", "created_at"]:
                setattr(doc, key, value)
        
        await self.db.commit()
        return True
    
    async def delete(self, doc_id: str) -> bool:
        """删除文档 (软删除)"""
        
        from datetime import datetime
        
        result = await self.db.execute(
            select(Document).where(Document.id == doc_id)
        )
        doc = result.scalar_one_or_none()
        
        if not doc:
            return False
        
        doc.deleted_at = datetime.utcnow()
        await self.db.commit()
        return True
    
    async def mark_indexed(self, doc_id: str):
        """标记为已索引"""
        
        from datetime import datetime
        
        result = await self.db.execute(
            select(Document).where(Document.id == doc_id)
        )
        doc = result.scalar_one_or_none()
        
        if doc:
            doc.indexed_at = datetime.utcnow()
            await self.db.commit()
    
    async def get_statistics(self) -> Dict:
        """获取统计信息"""
        
        from sqlalchemy import func
        
        # 文档总数
        total = await self.db.execute(
            select(func.count()).select_from(
                Document.where(Document.deleted_at.is_(None))
            )
        )
        total_count = total.scalar() or 0
        
        # 分类统计
        category_stats = await self.db.execute(
            select(
                Document.category_id,
                func.count()
            )
            .where(
                Document.deleted_at.is_(None),
                Document.category_id.isnot(None)
            )
            .group_by(Document.category_id)
        )
        
        category_distribution = {
            row[0]: row[1] 
            for row in category_stats.fetchall()
        }
        
        # 状态统计
        status_stats = await self.db.execute(
            select(
                Document.status,
                func.count()
            )
            .where(Document.deleted_at.is_(None))
            .group_by(Document.status)
        )
        
        status_distribution = {
            row[0]: row[1] 
            for row in status_stats.fetchall()
        }
        
        return {
            "total_documents": total_count,
            "by_category": category_distribution,
            "by_status": status_distribution
        }
    
    async def execute(self, query):
        """执行查询"""
        return await self.db.execute(query)
