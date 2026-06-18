"""知识图谱服务"""
from typing import List, Optional
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.models import KnowledgeNode, KnowledgeRelation, Document
from app.services.ai_service import ai_service


class KnowledgeService:
    """知识图谱服务"""

    # 实体类型映射
    ENTITY_TYPES = {
        "concept": "概念",
        "entity": "实体",
        "topic": "主题",
        "method": "方法",
        "tool": "工具"
    }

    # 关系类型
    RELATION_TYPES = {
        "relates_to": "相关",
        "prerequisite_of": "前置",
        "part_of": "部分",
        "derived_from": "衍生",
        "applies_to": "应用"
    }

    @staticmethod
    def extract_entities(text: str) -> List[dict]:
        """从文本中提取实体（简化版：基于规则）"""
        entities = []

        # 提取引号中的内容作为概念
        quoted = re.findall(r'[""「」『』]([^""「」『』]+)[""「」『』]', text)
        for item in quoted[:5]:
            entities.append({
                "name": item,
                "type": "concept",
                "description": f"文档中提到的概念：{item}"
            })

        # 提取可能的专有名词（大写字母开头的英文单词组合）
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        for item in list(set(proper_nouns))[:5]:
            if len(item) > 2:
                entities.append({
                    "name": item,
                    "type": "entity",
                    "description": f"文档中提到的实体：{item}"
                })

        # 提取关键词作为主题
        keywords = ai_service.extract_keywords(text) if hasattr(ai_service, 'extract_keywords') else []
        for keyword in keywords[:5]:
            entities.append({
                "name": keyword,
                "type": "topic",
                "description": f"文档讨论的主题：{keyword}"
            })

        return entities[:15]  # 限制最多 15 个实体

    @staticmethod
    async def build_knowledge_graph(
        db: AsyncSession,
        user_id: str,
        document_id: str,
        text: str
    ) -> List[KnowledgeNode]:
        """为文档构建知识图谱"""
        # 提取实体
        entities = KnowledgeService.extract_entities(text)

        # 创建知识节点
        nodes = []
        for entity in entities:
            node = KnowledgeNode(
                user_id=user_id,
                document_id=document_id,
                node_type=entity["type"],
                name=entity["name"],
                description=entity.get("description", ""),
                importance=0.5
            )
            db.add(node)
            nodes.append(node)

        await db.commit()

        # 为每个节点刷新以获取 ID
        for node in nodes:
            await db.refresh(node)

        # 创建节点之间的关系
        for i, node in enumerate(nodes):
            for j, other_node in enumerate(nodes):
                if i < j:
                    # 为相邻的节点创建关系
                    relation = KnowledgeRelation(
                        source_id=node.id,
                        target_id=other_node.id,
                        relation_type="relates_to",
                        weight=0.5
                    )
                    db.add(relation)

        await db.commit()
        return nodes

    @staticmethod
    async def get_user_knowledge_graph(
        db: AsyncSession,
        user_id: str,
        document_id: Optional[str] = None
    ) -> dict:
        """获取用户的知识图谱"""
        # 查询节点
        query = select(KnowledgeNode).where(KnowledgeNode.user_id == user_id)
        if document_id:
            query = query.where(KnowledgeNode.document_id == document_id)

        result = await db.execute(query)
        nodes = result.scalars().all()

        # 获取节点 ID 列表
        node_ids = [node.id for node in nodes]

        # 查询关系
        if node_ids:
            relations_query = select(KnowledgeRelation).where(
                and_(
                    KnowledgeRelation.source_id.in_(node_ids),
                    KnowledgeRelation.target_id.in_(node_ids)
                )
            )
            relations_result = await db.execute(relations_query)
            relations = relations_result.scalars().all()
        else:
            relations = []

        return {
            "nodes": nodes,
            "edges": relations
        }

    @staticmethod
    async def find_related_concepts(
        db: AsyncSession,
        user_id: str,
        concept_name: str
    ) -> List[KnowledgeNode]:
        """查找相关概念"""
        query = select(KnowledgeNode).where(
            and_(
                KnowledgeNode.user_id == user_id,
                KnowledgeNode.name.ilike(f"%{concept_name}%")
            )
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    def format_graph_for_visualization(graph_data: dict) -> dict:
        """格式化图谱数据用于可视化"""
        nodes = []
        for node in graph_data["nodes"]:
            nodes.append({
                "id": node.id,
                "label": node.name,
                "type": node.node_type,
                "description": node.description,
                "importance": node.importance
            })

        edges = []
        for edge in graph_data["edges"]:
            edges.append({
                "id": edge.id,
                "source": edge.source_id,
                "target": edge.target_id,
                "type": edge.relation_type,
                "weight": edge.weight
            })

        return {
            "nodes": nodes,
            "edges": edges
        }


knowledge_service = KnowledgeService()
