"""
天一阁 - AI 分类服务

基于大模型的文档分类
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import Document, Category
from ..core.config import settings


class ClassifierService:
    """AI 分类服务"""
    
    def __init__(self, db: AsyncSession, llm_provider: str = "openai"):
        self.db = db
        self.llm_provider = llm_provider
    
    async def classify_document(
        self,
        document: Document,
        force: bool = False
    ) -> Dict:
        """
        对文档进行分类
        
        Args:
            document: 文档对象
            force: 是否强制重新分类
            
        Returns:
            Dict: 分类结果
        """
        
        # 如果已有分类且未强制，重新分类则跳过
        if document.category_id and not force:
            return {
                "category_id": document.category_id,
                "category_path": document.category_path,
                "confidence": 1.0,
                "cached": True
            }
        
        # 提取文档特征
        features = self._extract_features(document)
        
        # 获取候选分类
        candidates = await self._get_candidate_categories()
        
        # AI 分类
        result = await self._llm_classify(features, candidates)
        
        # 更新文档
        if result.get("category_id"):
            await self._update_document_category(document.id, result)
        
        return result
    
    def _extract_features(self, document: Document) -> Dict[str, Any]:
        """提取文档特征"""
        
        return {
            "title": document.title or "",
            "file_name": document.file_name or "",
            "authors": document.authors or [],
            "keywords": document.keywords or [],
            "abstract": document.abstract or "",
            "content_preview": (document.content_text or "")[:1000],
            "extension": document.extension or "",
            "language": document.language or "zh"
        }
    
    async def _get_candidate_categories(self) -> List[Dict]:
        """获取候选分类"""
        
        result = await self.db.execute(
            select(Category).order_by(Category.path)
        )
        categories = result.scalars().all()
        
        return [
            {
                "id": cat.id,
                "name": cat.name,
                "path": cat.path,
                "type": cat.type
            }
            for cat in categories
        ]
    
    async def _llm_classify(
        self,
        features: Dict,
        candidates: List[Dict]
    ) -> Dict:
        """使用 LLM 进行分类"""
        
        # 构建提示词
        prompt = self._build_prompt(features, candidates)
        
        try:
            # 调用 LLM (这里用模拟)
            response = await self._call_llm(prompt)
            result = self._parse_response(response)
            return result
        except Exception as e:
            print(f"LLM 分类失败: {e}")
            return {
                "category_id": None,
                "category_path": "/未分类",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _build_prompt(
        self,
        features: Dict,
        candidates: List[Dict]
    ) -> str:
        """构建分类提示词"""
        
        prompt = f"""请根据以下文档信息，从候选分类中选择最合适的分类。

文档信息:
- 标题: {features.get('title', '未知')[:200]}
- 文件名: {features.get('file_name', '未知')}
- 摘要: {features.get('abstract', '无')[:500]}

候选分类:
"""
        
        for cat in candidates:
            prompt += f"- {cat['path']} ({cat['type']})\n"
        
        prompt += """
请返回最合适的分类路径和置信度:
{"category_path": "/分类路径", "confidence": 0.95}
"""
        
        return prompt
    
    async def _call_llm(self, prompt: str) -> str:
        """调用 LLM API"""
        
        # TODO: 集成 OpenAI/Anthropic API
        # 目前返回模拟结果
        import json
        
        if candidates := self._get_candidate_categories_sync():
            if len(candidates) > 1:
                return json.dumps({
                    "category_path": candidates[1].get("path", "/未分类"),
                    "confidence": 0.85
                })
        
        return '{"category_path": "/未分类", "confidence": 0.5}'
    
    def _get_candidate_categories_sync(self) -> List[Dict]:
        """同步获取候选分类"""
        # 简化实现
        return [{"path": "/未分类", "type": "system"}]
    
    def _parse_response(self, response: str) -> Dict:
        """解析 LLM 返回结果"""
        
        import json
        
        try:
            result = json.loads(response)
            return {
                "category_path": result.get("category_path", "/未分类"),
                "confidence": result.get("confidence", 0.0)
            }
        except json.JSONDecodeError:
            return {
                "category_path": "/未分类",
                "confidence": 0.5
            }
    
    async def _update_document_category(
        self,
        doc_id: str,
        result: Dict
    ) -> bool:
        """更新文档分类"""
        
        from datetime import datetime
        
        result = await self.db.execute(
            select(Document).where(Document.id == doc_id)
        )
        doc = result.scalar_one_or_none()
        
        if not doc:
            return False
        
        # 查找分类 ID
        cat_result = await self.db.execute(
            select(Category).where(
                Category.path == result["category_path"]
            )
        )
        category = cat_result.scalar_one_or_none()
        
        if category:
            doc.category_id = category.id
            doc.category_path = category.path
            doc.status = "classified"
            doc.updated_at = datetime.utcnow()
            await self.db.commit()
        
        return True
