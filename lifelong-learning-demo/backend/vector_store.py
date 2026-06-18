import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import uuid
import logging
from sentence_transformers import SentenceTransformer
import numpy as np

from models import DocumentChunk

logger = logging.getLogger(__name__)


class VectorStore:
    """向量存储服务"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        
        # 初始化ChromaDB客户端
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 初始化embedding模型（使用本地BGE模型）
        try:
            self.embedding_model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
            logger.info("BGE-small-zh embedding模型加载成功")
        except Exception as e:
            logger.warning(f"BGE模型加载失败，使用随机embedding: {e}")
            self.embedding_model = None
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name="document_chunks",
            metadata={"description": "文档分块向量存储"}
        )
    
    def get_embedding(self, text: str) -> List[float]:
        """获取文本的embedding向量"""
        if self.embedding_model:
            # 使用BGE模型
            embedding = self.embedding_model.encode(text).tolist()
        else:
            # 备用：随机embedding（仅用于演示）
            embedding = np.random.randn(384).tolist()  # BGE-small维度是384
        
        return embedding
    
    def add_document_chunks(self, document_id: str, chunks: List[DocumentChunk]) -> List[str]:
        """添加文档分块到向量数据库"""
        if not chunks:
            return []
        
        # 准备数据
        ids = []
        embeddings = []
        metadatas = []
        documents = []
        
        for chunk in chunks:
            chunk_id = str(uuid.uuid4())
            ids.append(chunk_id)
            
            # 获取embedding
            embedding = self.get_embedding(chunk.chunk_text)
            embeddings.append(embedding)
            
            # 准备元数据
            metadata = {
                "document_id": str(document_id),
                "chunk_index": chunk.chunk_index,
                "chunk_id": str(chunk.id) if chunk.id else chunk_id,
                "source": "document"
            }
            metadatas.append(metadata)
            
            # 存储文本
            documents.append(chunk.chunk_text)
        
        # 添加到集合
        try:
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"成功添加 {len(chunks)} 个分块到向量数据库")
            return ids
        except Exception as e:
            logger.error(f"添加分块到向量数据库失败: {e}")
            raise
    
    def search_similar(self, query: str, limit: int = 10, 
                      document_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """搜索相似的文档分块"""
        try:
            # 获取查询的embedding
            query_embedding = self.get_embedding(query)
            
            # 构建过滤条件
            where_filter = None
            if document_ids:
                where_filter = {
                    "$or": [
                        {"document_id": doc_id} for doc_id in document_ids
                    ]
                }
            
            # 执行搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            # 格式化结果
            formatted_results = []
            if results['documents']:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "score": 1.0 - results['distances'][0][i] if results['distances'] else 0.0,
                        "distance": results['distances'][0][i] if results['distances'] else None
                    })
            
            return formatted_results
        except Exception as e:
            logger.error(f"向量搜索失败: {e}")
            return []
    
    def delete_document_chunks(self, document_id: str) -> int:
        """删除指定文档的所有分块"""
        try:
            # 获取文档的所有分块
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if results['ids']:
                # 删除这些分块
                self.collection.delete(ids=results['ids'])
                logger.info(f"删除文档 {document_id} 的 {len(results['ids'])} 个分块")
                return len(results['ids'])
            return 0
        except Exception as e:
            logger.error(f"删除文档分块失败: {e}")
            return 0
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "collection_name": self.collection.name,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            logger.error(f"获取集合统计失败: {e}")
            return {"error": str(e)}
    
    def clear_collection(self) -> bool:
        """清空集合"""
        try:
            self.collection.delete(where={})
            logger.info("向量数据库集合已清空")
            return True
        except Exception as e:
            logger.error(f"清空集合失败: {e}")
            return False


class KnowledgeRetriever:
    """知识检索器"""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
    
    def retrieve_relevant_chunks(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """检索相关的文档分块"""
        results = self.vector_store.search_similar(query, limit=limit)
        
        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def build_context(self, query: str, max_chunks: int = 3) -> str:
        """构建检索增强的上下文"""
        relevant_chunks = self.retrieve_relevant_chunks(query, limit=max_chunks)
        
        if not relevant_chunks:
            return ""
        
        # 构建上下文
        context_parts = []
        for i, chunk in enumerate(relevant_chunks):
            context_parts.append(f"[来源 {i+1}]: {chunk['text']}")
        
        return "\n\n".join(context_parts)


# 单例实例
vector_store = VectorStore()
knowledge_retriever = KnowledgeRetriever(vector_store)