# Qdrant Vector Database Integration
#Qdrant 向量数据库集成

from typing import List, Dict, Any, Optional
from ..core.config import settings
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams, Distance, PointStruct,
    Filter, FieldCondition, MatchValue
)
import numpy as np
import uuid


class VectorDatabase:
    """
    Qdrant 向量数据库服务
    
    提供文档向量的存储、检索和管理
    """
    
    def __init__(
        self,
        url: str = None,
        api_key: str = None,
        collection_name: str = "documents"
    ):
        self.url = url or settings.QDRANT_URL
        self.api_key = api_key or settings.QDRANT_API_KEY
        self.collection_name = collection_name
        
        # 初始化客户端
        if self.api_key:
            self.client = QdrantClient(
                url=self.url,
                api_key=self.api_key
            )
        else:
            self.client = QdrantClient(url=self.url)
        
        # 嵌入维度 (BGE-large: 1024)
        self.vector_size = 1024
        self.distance = Distance.COSINE
    
    async def create_collection(self, vector_size: int = None):
        """
        创建向量集合
        
        Args:
            vector_size: 向量维度
        """
        
        size = vector_size or self.vector_size
        
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=size,
                distance=self.distance,
                on_disk=True
            ),
            # 优化配置
            optimizers_config={
                "deleted_threshold": 0.2,
                "vacuum_min_vector_number": 1000,
                "default_segment_number": 2
            }
        )
        
        print(f"✓ 创建向量集合: {self.collection_name}")
    
    async def ensure_collection(self):
        """确保集合存在"""
        
        collections = self.client.get_collections().collections
        
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            await self.create_collection()
    
    async def add_documents(
        self,
        document_ids: List[str],
        texts: List[str],
        vectors: List[List[float]] = None,
        metadata: List[Dict] = None
    ):
        """
        添加文档向量
        
        Args:
            document_ids: 文档 ID 列表
            texts: 文本内容列表
            vectors: 向量列表 (可选，自动计算)
            metadata: 元数据列表
        """
        
        await self.ensure_collection()
        
        if vectors is None and texts:
            # 自动计算向量
            from .embedding import get_embedding_service
            embedding_service = get_embedding_service()
            vectors = await embedding_service.encode(texts)
        
        # 构建 points
        points = []
        
        for i, doc_id in enumerate(document_ids):
            point = PointStruct(
                id=doc_id,
                vector=vectors[i] if vectors else [],
                payload={
                    "text": texts[i] if texts else "",
                    "document_id": doc_id,
                    **(metadata[i] if metadata else {})
                }
            )
            points.append(point)
        
        # 批量上传
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True
        )
        
        print(f"✓ 添加 {len(points)} 个文档向量")
    
    async def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        filter_document_ids: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        向量搜索
        
        Args:
            query_vector: 查询向量
            limit: 返回数量
            filter_document_ids: 文档 ID 过滤
            
        Returns:
            List[Dict]: 搜索结果
        """
        
        await self.ensure_collection()
        
        # 构建过滤条件
        filter_condition = None
        if filter_document_ids:
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=filter_document_ids[0])
                    )
                ]
            )
        
        # 执行搜索
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=filter_condition,
            with_payload=True,
            with_vectors=False
        )
        
        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload
            }
            for hit in results
        ]
    
    async def search_text(
        self,
        query_text: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        语义搜索 (文本输入)
        
        Args:
            query_text: 查询文本
            limit: 返回数量
            
        Returns:
            List[Dict]: 搜索结果
        """
        
        # 计算查询向量
        from .embedding import get_embedding_service
        embedding_service = get_embedding_service()
        
        query_vector = (await embedding_service.encode([query_text]))[0]
        
        return await self.search(query_vector, limit)
    
    async def delete_document(self, document_id: str):
        """删除文档向量"""
        
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=[document_id],
            wait=True
        )
    
    async def delete_collection(self):
        """删除集合"""
        
        self.client.delete_collection(self.collection_name)
        print(f"✓ 删除向量集合: {self.collection_name}")
    
    async def get_collection_info(self) -> Dict:
        """获取集合信息"""
        
        collection_info = self.client.get_collection(self.collection_name)
        
        return {
            "name": collection_info.config.params.vector_params.size,
            "distance": str(collection_info.config.params.vector_params.distance),
            "status": collection_info.status,
            "points_count": collection_info.points_count
        }
    
    async def list_collections(self) -> List[str]:
        """列出所有集合"""
        
        collections = self.client.get_collections().collections
        return [c.name for c in collections]


# 全局实例
vector_db = None


def get_vector_db() -> VectorDatabase:
    """获取向量数据库实例"""
    global vector_db
    
    if vector_db is None:
        vector_db = VectorDatabase()
    
    return vector_db
