# RAG Engine - Retrieval-Augmented Generation
# RAG 引擎 - 检索增强生成

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re
import json
from ..core.config import settings
from .embedding import get_embedding_service
from .vector_db import get_vector_db
from .llm import get_llm


class RetrievalStrategy(Enum):
    """检索策略"""
    VECTOR_ONLY = "vector_only"
    KEYWORD_ONLY = "keyword_only"
    HYBRID = "hybrid"


class RerankStrategy(Enum):
    """重排序策略"""
    NONE = "none"
    SIMPLE = "simple"
    LLAMA_INDEX = "llama_index"
    CROSS_ENCODER = "cross_encoder"


@dataclass
class RetrievedDocument:
    """检索到的文档"""
    id: str
    title: str
    content: str
    score: float
    metadata: Dict[str, Any] = None


@dataclass
class RAGResponse:
    """RAG 响应"""
    answer: str
    sources: List[RetrievedDocument]
    reasoning: str = ""
    confidence: float = 0.0


class RAGEngine:
    """
    RAG 引擎 - 检索增强生成
    
    负责文档检索、上下文构建、答案生成
    """
    
    def __init__(
        self,
        retrieval_strategy: RetrievalStrategy = RetrievalStrategy.HYBRID,
        rerank_strategy: RerankStrategy = RerankStrategy.SIMPLE,
        top_k: int = None,
        similarity_threshold: float = None
    ):
        """
        初始化 RAG 引擎
        
        Args:
            retrieval_strategy: 检索策略
            rerank_strategy: 重排序策略
            top_k: 检索数量
            similarity_threshold: 相似度阈值
        """
        self.retrieval_strategy = retrieval_strategy
        self.rerank_strategy = rerank_strategy
        self.top_k = top_k or settings.RETRIEVAL_TOP_K
        self.similarity_threshold = similarity_threshold or settings.RETRIEVAL_SIMILARITY_THRESHOLD
        
        # 获取服务实例
        self.embedding_service = get_embedding_service()
        self.vector_db = get_vector_db()
        self.llm = get_llm()
    
    async def query(
        self,
        question: str,
        document_ids: List[str] = None,
        category_ids: List[int] = None,
        tags: List[str] = None,
        include_metadata: bool = True
    ) -> RAGResponse:
        """
        RAG 查询
        
        Args:
            question: 用户问题
            document_ids: 文档 ID 过滤
            category_ids: 分类 ID 过滤
            tags: 标签过滤
            include_metadata: 是否包含元数据
            
        Returns:
            RAGResponse: RAG 响应
        """
        # 1. 理解问题
        query_analysis = await self._analyze_query(question)
        
        # 2. 检索文档
        retrieved_docs = await self._retrieve_documents(
            question=question,
            query_analysis=query_analysis,
            document_ids=document_ids,
            category_ids=category_ids,
            tags=tags
        )
        
        # 3. 重排序
        if self.rerank_strategy != RerankStrategy.NONE:
            retrieved_docs = await self._rerank_documents(
                question,
                retrieved_docs
            )
        
        # 4. 过滤低质量结果
        filtered_docs = [
            doc for doc in retrieved_docs
            if doc.score >= self.similarity_threshold
        ]
        
        # 5. 生成答案
        answer, reasoning = await self._generate_answer(
            question=question,
            documents=filtered_docs,
            query_analysis=query_analysis
        )
        
        # 6. 计算置信度
        confidence = self._calculate_confidence(filtered_docs, answer)
        
        return RAGResponse(
            answer=answer,
            sources=filtered_docs,
            reasoning=reasoning,
            confidence=confidence
        )
    
    async def _analyze_query(self, question: str) -> Dict[str, Any]:
        """
        分析用户问题
        
        Args:
            question: 用户问题
            
        Returns:
            Dict: 问题分析结果
        """
        # 提取关键词
        keywords = self._extract_keywords(question)
        
        # 识别问题类型
        question_type = self._classify_question_type(question)
        
        # 确定需要的文档类型
        required_domains = self._identify_required_domains(question)
        
        return {
            "keywords": keywords,
            "question_type": question_type,
            "required_domains": required_domains,
            "original_question": question
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单实现：移除停用词，提取名词和动词
        # 实际项目中可以使用 jieba 或 spaCy
        
        # 中文停用词
        stop_words = {
            "的", "了", "在", "是", "我", "有", "和", "就",
            "不", "人", "都", "一", "一个", "上", "也", "很",
            "到", "说", "要", "去", "你", "会", "着", "没有",
            "看", "好", "自己", "这", "那", "什么", "怎么", "为什么"
        }
        
        # 简单分词（按空格和标点）
        words = re.findall(r'[\w\u4e00-\u9fff]+', text)
        
        # 过滤停用词
        keywords = [word for word in words if word not in stop_words and len(word) > 1]
        
        return keywords
    
    def _classify_question_type(self, question: str) -> str:
        """分类问题类型"""
        question = question.lower()
        
        if any(q in question for q in ["什么是", "介绍", "解释", "定义"]):
            return "explanation"
        elif any(q in question for q in ["怎么做", "如何", "方法"]):
            return "how_to"
        elif any(q in question for q in ["为什么", "原因"]):
            return "reason"
        elif any(q in question for q in ["比较", "区别", "对比"]):
            return "comparison"
        elif any(q in question for q in ["总结", "概括", "要点"]):
            return "summary"
        else:
            return "general"
    
    def _identify_required_domains(self, question: str) -> List[str]:
        """识别需要的领域"""
        # 简单实现，实际可以用分类器
        domains = []
        
        domain_keywords = {
            "技术": ["代码", "编程", "开发", "API", "技术", "软件"],
            "业务": ["流程", "规范", "政策", "制度", "业务"],
            "管理": ["管理", "组织", "团队", "项目"],
            "法律": ["法律", "合同", "条款", "合规"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in question for keyword in keywords):
                domains.append(domain)
        
        return domains if domains else ["general"]
    
    async def _retrieve_documents(
        self,
        question: str,
        query_analysis: Dict[str, Any],
        document_ids: List[str] = None,
        category_ids: List[int] = None,
        tags: List[str] = None
    ) -> List[RetrievedDocument]:
        """
        检索文档
        
        Args:
            question: 用户问题
            query_analysis: 问题分析
            document_ids: 文档 ID 过滤
            category_ids: 分类 ID 过滤
            tags: 标签过滤
            
        Returns:
            List[RetrievedDocument]: 检索到的文档
        """
        all_docs = []
        
        # 根据策略执行检索
        if self.retrieval_strategy in [RetrievalStrategy.VECTOR_ONLY, RetrievalStrategy.HYBRID]:
            vector_docs = await self._vector_search(question, document_ids)
            all_docs.extend(vector_docs)
        
        if self.retrieval_strategy in [RetrievalStrategy.KEYWORD_ONLY, RetrievalStrategy.HYBRID]:
            keyword_docs = await self._keyword_search(
                query_analysis["keywords"],
                document_ids,
                category_ids,
                tags
            )
            all_docs.extend(keyword_docs)
        
        # 去重
        seen_ids = set()
        unique_docs = []
        for doc in all_docs:
            if doc.id not in seen_ids:
                seen_ids.add(doc.id)
                unique_docs.append(doc)
        
        # 排序并返回 top_k
        unique_docs.sort(key=lambda x: x.score, reverse=True)
        return unique_docs[:self.top_k]
    
    async def _vector_search(
        self,
        question: str,
        document_ids: List[str] = None
    ) -> List[RetrievedDocument]:
        """向量搜索"""
        # 编码查询
        query_vector = (await self.embedding_service.encode([question]))[0]
        
        # 搜索
        results = await self.vector_db.search(
            query_vector=query_vector,
            limit=self.top_k * 2,
            filter_document_ids=document_ids
        )
        
        # 转换为 RetrievedDocument
        docs = []
        for result in results:
            payload = result.get("payload", {})
            docs.append(RetrievedDocument(
                id=str(result["id"]),
                title=payload.get("title", "Untitled"),
                content=payload.get("text", ""),
                score=result["score"],
                metadata=payload
            ))
        
        return docs
    
    async def _keyword_search(
        self,
        keywords: List[str],
        document_ids: List[str] = None,
        category_ids: List[int] = None,
        tags: List[str] = None
    ) -> List[RetrievedDocument]:
        """关键词搜索"""
        # 这里需要连接到数据库进行全文搜索
        # 简单实现：返回空列表，实际项目中需要实现
        from ..models.document import Document
        from ..core.database import get_db
        
        docs = []
        try:
            # 尝试从数据库搜索
            # 这里只是示意，实际需要实现
            pass
        except Exception as e:
            print(f"Keyword search error: {e}")
        
        return docs
    
    async def _rerank_documents(
        self,
        question: str,
        documents: List[RetrievedDocument]
    ) -> List[RetrievedDocument]:
        """
        重排序文档
        
        Args:
            question: 用户问题
            documents: 检索到的文档
            
        Returns:
            List[RetrievedDocument]: 重排序后的文档
        """
        if self.rerank_strategy == RerankStrategy.SIMPLE:
            return await self._simple_rerank(question, documents)
        elif self.rerank_strategy == RerankStrategy.CROSS_ENCODER:
            return await self._cross_encoder_rerank(question, documents)
        else:
            return documents
    
    async def _simple_rerank(
        self,
        question: str,
        documents: List[RetrievedDocument]
    ) -> List[RetrievedDocument]:
        """简单重排序"""
        # 计算简单的匹配分数
        question_lower = question.lower()
        
        for doc in documents:
            # 关键词匹配加分
            content_lower = doc.content.lower()
            match_count = sum(1 for word in question_lower.split() if word in content_lower)
            
            # 长度偏好（适中长度）
            content_length = len(doc.content)
            length_score = 0.0
            if 100 <= content_length <= 2000:
                length_score = 0.1
            elif content_length > 2000:
                length_score = 0.05
            
            # 更新分数
            doc.score = doc.score * 0.7 + (match_count / max(len(question_lower.split()), 1)) * 0.2 + length_score
        
        # 重新排序
        documents.sort(key=lambda x: x.score, reverse=True)
        return documents
    
    async def _cross_encoder_rerank(
        self,
        question: str,
        documents: List[RetrievedDocument]
    ) -> List[RetrievedDocument]:
        """Cross-Encoder 重排序"""
        # 需要 sentence-transformers 的 CrossEncoder
        try:
            from sentence_transformers import CrossEncoder
            
            model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            
            # 构建 pairs
            pairs = [[question, doc.content] for doc in documents]
            
            # 预测
            scores = model.predict(pairs)
            
            # 更新分数
            for doc, score in zip(documents, scores):
                doc.score = float(score)
            
            # 排序
            documents.sort(key=lambda x: x.score, reverse=True)
            
        except ImportError:
            print("⚠️ CrossEncoder not available, using simple rerank")
            return await self._simple_rerank(question, documents)
        
        return documents
    
    async def _generate_answer(
        self,
        question: str,
        documents: List[RetrievedDocument],
        query_analysis: Dict[str, Any]
    ) -> tuple[str, str]:
        """
        生成答案
        
        Args:
            question: 用户问题
            documents: 检索到的文档
            query_analysis: 问题分析
            
        Returns:
            tuple: (answer, reasoning)
        """
        if not documents:
            return (
                "抱歉，我没有找到相关的文档来回答您的问题。请尝试重新表述问题，或者检查是否有相关文档已上传。",
                "没有检索到相关文档"
            )
        
        # 构建上下文
        context = self._build_context(documents)
        
        # 构建提示词
        system_prompt = self._build_system_prompt(query_analysis)
        user_prompt = self._build_user_prompt(question, context)
        
        # 调用 LLM
        try:
            response = await self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=2000
            )
            
            # 解析响应
            answer, reasoning = self._parse_llm_response(response)
            
            return answer, reasoning
            
        except Exception as e:
            print(f"LLM generation error: {e}")
            return (
                "抱歉，生成答案时出现了问题。请稍后再试。",
                f"生成错误: {str(e)}"
            )
    
    def _build_context(self, documents: List[RetrievedDocument]) -> str:
        """构建上下文"""
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            context_part = f"""
文档 {i}:
标题: {doc.title}
内容: {doc.content[:3000]}  # 限制长度
来源: {doc.metadata.get('source', 'Unknown') if doc.metadata else 'Unknown'}
---
"""
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _build_system_prompt(self, query_analysis: Dict[str, Any]) -> str:
        """构建系统提示词"""
        question_type = query_analysis.get("question_type", "general")
        
        base_prompt = """你是一个专业的知识助手，名为"天一阁"。你的任务是基于提供的文档内容，准确、客观地回答用户的问题。

回答原则:
1. **基于文档**: 只使用提供的文档内容，不要编造信息
2. **引用来源**: 在回答中标注信息来源（如"根据文档1"）
3. **诚实**: 如果文档中没有相关信息，明确说明
4. **清晰**: 回答要条理清晰，易于理解
5. **客观**: 保持中立，不添加个人观点
"""
        
        # 根据问题类型调整提示词
        if question_type == "explanation":
            base_prompt += "\n这是一个概念解释类问题，请给出清晰的定义和说明。"
        elif question_type == "how_to":
            base_prompt += "\n这是一个操作指南类问题，请分步骤说明。"
        elif question_type == "summary":
            base_prompt += "\n这是一个总结类问题，请提炼核心要点。"
        
        base_prompt += """

请用 JSON 格式返回，包含以下字段:
- answer: 回答内容（字符串）
- reasoning: 推理过程（字符串，可选）
"""
        
        return base_prompt
    
    def _build_user_prompt(self, question: str, context: str) -> str:
        """构建用户提示词"""
        return f"""请基于以下文档内容回答问题：

问题：{question}

相关文档：
{context}

请给出答案。"""
    
    def _parse_llm_response(self, response: str) -> tuple[str, str]:
        """解析 LLM 响应"""
        try:
            # 尝试解析 JSON
            import json
            result = json.loads(response)
            answer = result.get("answer", "")
            reasoning = result.get("reasoning", "")
            return answer, reasoning
        except:
            # 如果不是 JSON，直接返回
            return response, ""
    
    def _calculate_confidence(self, documents: List[RetrievedDocument], answer: str) -> float:
        """计算置信度"""
        if not documents:
            return 0.0
        
        # 基于文档分数计算
        avg_score = sum(doc.score for doc in documents) / len(documents)
        
        # 基于答案长度（太短可能质量低）
        length_factor = min(len(answer) / 100, 1.0)
        
        # 综合计算
        confidence = avg_score * 0.7 + length_factor * 0.3
        
        return min(confidence, 1.0)


# 全局实例
_rag_engine = None


def get_rag_engine() -> RAGEngine:
    """获取 RAG 引擎实例"""
    global _rag_engine
    
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    
    return _rag_engine