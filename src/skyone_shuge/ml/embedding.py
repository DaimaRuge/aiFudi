# Text Embedding Service
#文本向量化服务

from typing import List, Dict, Any, Optional
from ..core.config import settings
import numpy as np


class EmbeddingService:
    """
    文本向量化服务
    
    支持多种 embedding 模型
    """
    
    def __init__(self, model_name: str = None, device: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.device = device or settings.EMBEDDING_DEVICE
        self.model = None
        self.client = None
    
    async def load_model(self):
        """加载 embedding 模型"""
        
        # 优先使用本地模型
        if self.model_name.startswith("BAAI/"):
            await self._load_local_model()
        else:
            await self._load_api_model()
    
    async def _load_local_model(self):
        """加载本地 HuggingFace 模型"""
        
        try:
            from sentence_transformers import SentenceTransformer
            
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device
            )
            print(f"✓ 加载本地模型: {self.model_name}")
            
        except ImportError:
            print("⚠️ sentence-transformers 未安装，回退到 API")
            await self._load_api_model()
    
    async def _load_api_model(self):
        """加载 API 模型 (OpenAI)"""
        
        from ..ml.llm import OpenAILLM
        self.client = OpenAILLM()
        print(f"✓ 使用 OpenAI Embedding API")
    
    async def encode(
        self,
        texts: List[str],
        normalize: bool = True,
        batch_size: int = 32
    ) -> List[List[float]]:
        """
        文本编码为向量
        
        Args:
            texts: 文本列表
            normalize: 是否归一化
            batch_size: 批处理大小
            
        Returns:
            List[List[float]]: 向量列表
        """
        
        if self.model is not None:
            return await self._encode_local(texts, normalize, batch_size)
        elif self.client is not None:
            return await self._encode_api(texts)
        else:
            # 自动加载
            await self.load_model()
            return await self.encode(texts, normalize, batch_size)
    
    async def _encode_local(
        self,
        texts: List[str],
        normalize: bool,
        batch_size: int
    ) -> List[List[float]]:
        """本地模型编码"""
        
        import asyncio
        
        # 批量处理
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # 在线程池中运行
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: self.model.encode(batch, normalize_embeddings=normalize)
            )
            
            all_embeddings.extend(embeddings.tolist())
        
        return all_embeddings
    
    async def _encode_api(self, texts: List[str]) -> List[List[float]]:
        """API 模型编码"""
        
        return await self.client.embed(texts)
    
    async def similarity(
        self,
        texts1: List[str],
        texts2: List[str]
    ) -> List[List[float]]:
        """
        计算文本相似度矩阵
        
        Args:
            texts1: 第一组文本
            texts2: 第二组文本
            
        Returns:
            List[List[float]]: 相似度矩阵
        """
        
        # 编码两组文本
        embeddings1 = await self.encode(texts1)
        embeddings2 = await self.encode(texts2)
        
        # 计算余弦相似度
        matrix = []
        for e1 in embeddings1:
            similarities = []
            norm1 = np.linalg.norm(e1)
            
            for e2 in embeddings2:
                norm2 = np.linalg.norm(e2)
                if norm1 * norm2 > 0:
                    sim = np.dot(e1, e2) / (norm1 * norm2)
                else:
                    sim = 0.0
                similarities.append(sim)
            
            matrix.append(similarities)
        
        return matrix
    
    async def search(
        self,
        query: str,
        documents: List[str],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        语义搜索
        
        Args:
            query: 查询文本
            documents: 文档列表
            top_k: 返回前 k 个结果
            
        Returns:
            List[Dict]: 搜索结果
        """
        
        # 编码查询
        query_embedding = (await self.encode([query]))[0]
        
        # 编码文档
        doc_embeddings = await self.encode(documents)
        
        # 计算相似度
        similarities = []
        query_norm = np.linalg.norm(query_embedding)
        
        for i, doc_emb in enumerate(doc_embeddings):
            doc_norm = np.linalg.norm(doc_emb)
            if query_norm * doc_norm > 0:
                sim = np.dot(query_embedding, doc_emb) / (query_norm * doc_norm)
            else:
                sim = 0.0
            
            similarities.append({
                "index": i,
                "document": documents[i],
                "score": sim
            })
        
        # 排序并返回 top_k
        similarities.sort(key=lambda x: x["score"], reverse=True)
        
        return similarities[:top_k]


# 全局实例
embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """获取向量化服务实例"""
    global embedding_service
    
    if embedding_service is None:
        embedding_service = EmbeddingService()
    
    return embedding_service
