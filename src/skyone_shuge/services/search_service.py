"""
天一阁 - 搜索服务
高级搜索：混合搜索、重排序、元数据过滤
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models.document import Document, DocumentChunk
from ..models.category import Category
from ..schemas.search import SearchQuery, SearchResult, SearchFilter
from ..ml.rag import get_rag_engine
from ..core.database import get_db
from sqlalchemy import select, and_, or_, text


class SearchService:
    """搜索服务"""
    
    def __init__(self):
        self.rag_engine = get_rag_engine()
    
    async def hybrid_search(
        self,
        query: SearchQuery
    ) -> List[SearchResult]:
        """
        混合搜索
        
        Args:
            query: 搜索查询
            
        Returns:
            List[SearchResult]: 搜索结果
        """
        # 1. 向量搜索
        vector_results = await self._vector_search(query)
        
        # 2. 关键词搜索
        keyword_results = await self._keyword_search(query)
        
        # 3. 合并结果
        combined_results = self._merge_results(vector_results, keyword_results)
        
        # 4. 重排序
        if query.enable_rerank:
            combined_results = await self._rerank_results(query.query, combined_results)
        
        # 5. 分页
        start_idx = (query.page - 1) * query.page_size
        end_idx = start_idx + query.page_size
        paginated_results = combined_results[start_idx:end_idx]
        
        return paginated_results
    
    async def _vector_search(
        self,
        query: SearchQuery
    ) -> List[SearchResult]:
        """向量搜索"""
        try:
            # 使用 RAG 引擎进行向量搜索
            rag_response = await self.rag_engine.query(
                question=query.query,
                document_ids=query.filters.document_ids if query.filters else None,
                category_ids=query.filters.category_ids if query.filters else None,
                tags=query.filters.tags if query.filters else None
            )
            
            # 转换为 SearchResult
            results = []
            for i, source in enumerate(rag_response.sources):
                results.append(SearchResult(
                    id=source.id,
                    title=source.title,
                    snippet=source.content[:200],
                    score=source.score,
                    search_type="vector",
                    metadata=source.metadata or {}
                ))
            
            return results
            
        except Exception as e:
            print(f"Vector search error: {e}")
            return []
    
    async def _keyword_search(
        self,
        query: SearchQuery
    ) -> List[SearchResult]:
        """关键词搜索"""
        try:
            async with get_db() as db:
                # 构建查询
                stmt = select(Document).where(
                    Document.title.contains(query.query) |
                    Document.description.contains(query.query)
                )
                
                # 应用过滤器
                if query.filters:
                    stmt = self._apply_filters(stmt, query.filters)
                
                # 执行查询
                result = await db.execute(stmt)
                documents = result.scalars().all()
                
                # 转换为 SearchResult
                results = []
                for doc in documents:
                    # 计算简单的匹配分数
                    title_match = query.query in doc.title
                    desc_match = query.query in (doc.description or "")
                    score = 0.8 if title_match else 0.5 if desc_match else 0.3
                    
                    results.append(SearchResult(
                        id=str(doc.id),
                        title=doc.title,
                        snippet=doc.description[:200] if doc.description else "",
                        score=score,
                        search_type="keyword",
                        metadata={
                            "document_id": doc.id,
                            "created_at": doc.created_at.isoformat() if doc.created_at else None,
                            "category_id": doc.category_id
                        }
                    ))
                
                return results
                
        except Exception as e:
            print(f"Keyword search error: {e}")
            return []
    
    def _apply_filters(self, stmt, filters: SearchFilter):
        """应用搜索过滤器"""
        conditions = []
        
        if filters.document_ids:
            conditions.append(Document.id.in_(filters.document_ids))
        
        if filters.category_ids:
            conditions.append(Document.category_id.in_(filters.category_ids))
        
        if filters.created_after:
            conditions.append(Document.created_at >= filters.created_after)
        
        if filters.created_before:
            conditions.append(Document.created_at <= filters.created_before)
        
        if filters.file_types:
            conditions.append(Document.file_type.in_(filters.file_types))
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        return stmt
    
    def _merge_results(
        self,
        vector_results: List[SearchResult],
        keyword_results: List[SearchResult]
    ) -> List[SearchResult]:
        """合并搜索结果"""
        # 创建 ID 到结果的映射
        result_map = {}
        
        # 添加向量结果
        for result in vector_results:
            result_map[result.id] = result
        
        # 添加关键词结果（合并分数）
        for result in keyword_results:
            if result.id in result_map:
                # 合并分数：取平均或加权
                existing = result_map[result.id]
                existing.score = (existing.score * 0.7 + result.score * 0.3)
                existing.search_type = "hybrid"
            else:
                result_map[result.id] = result
        
        # 转换为列表并排序
        merged = list(result_map.values())
        merged.sort(key=lambda x: x.score, reverse=True)
        
        return merged
    
    async def _rerank_results(
        self,
        query: str,
        results: List[SearchResult]
    ) -> List[SearchResult]:
        """重排序搜索结果"""
        try:
            # 使用 RAG 引擎的重排序功能
            from ..ml.rag import RetrievedDocument
            
            # 转换为 RetrievedDocument
            rag_docs = [
                RetrievedDocument(
                    id=result.id,
                    title=result.title,
                    content=result.snippet,
                    score=result.score,
                    metadata=result.metadata
                )
                for result in results
            ]
            
            # 重排序
            reranked_docs = await self.rag_engine._rerank_documents(query, rag_docs)
            
            # 转换回 SearchResult
            reranked_results = []
            for doc, original in zip(reranked_docs, results):
                reranked_results.append(SearchResult(
                    id=doc.id,
                    title=doc.title,
                    snippet=original.snippet,
                    score=doc.score,
                    search_type=original.search_type,
                    metadata=original.metadata
                ))
            
            return reranked_results
            
        except Exception as e:
            print(f"Rerank error: {e}")
            return results


# 全局实例
_search_service = None


def get_search_service() -> SearchService:
    """获取搜索服务实例"""
    global _search_service
    
    if _search_service is None:
        _search_service = SearchService()
    
    return _search_service
