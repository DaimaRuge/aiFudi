"""知识图谱 API 路由"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.models import User
from app.schemas.schemas import (
    KnowledgeGraphResponse,
    KnowledgeNodeResponse,
    KnowledgeRelationResponse
)
from app.services.knowledge_service import knowledge_service

router = APIRouter(prefix="/api/knowledge", tags=["知识图谱"])


@router.get("/graph", response_model=KnowledgeGraphResponse)
async def get_knowledge_graph(
    document_id: Optional[str] = Query(None, description="文档ID，不指定则返回所有"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取知识图谱"""
    graph_data = await knowledge_service.get_user_knowledge_graph(
        db, current_user.id, document_id
    )

    return KnowledgeGraphResponse(
        nodes=[KnowledgeNodeResponse.model_validate(n) for n in graph_data["nodes"]],
        edges=[KnowledgeRelationResponse.model_validate(e) for e in graph_data["edges"]]
    )


@router.get("/graph/visualization")
async def get_graph_for_visualization(
    document_id: Optional[str] = Query(None, description="文档ID，不指定则返回所有"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用于可视化的知识图谱数据"""
    graph_data = await knowledge_service.get_user_knowledge_graph(
        db, current_user.id, document_id
    )

    return knowledge_service.format_graph_for_visualization(graph_data)


@router.get("/search")
async def search_concepts(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """搜索知识概念"""
    nodes = await knowledge_service.find_related_concepts(
        db, current_user.id, q
    )

    return {
        "query": q,
        "results": [
            {
                "id": node.id,
                "name": node.name,
                "type": node.node_type,
                "description": node.description
            }
            for node in nodes
        ]
    }


@router.get("/stats")
async def get_knowledge_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取知识图谱统计信息"""
    from app.models.models import KnowledgeNode, KnowledgeRelation

    # 统计节点数量
    nodes_result = await db.execute(
        select(KnowledgeNode).where(KnowledgeNode.user_id == current_user.id)
    )
    nodes = nodes_result.scalars().all()

    # 按类型统计
    type_counts = {}
    for node in nodes:
        type_counts[node.node_type] = type_counts.get(node.node_type, 0) + 1

    # 统计关系数量
    node_ids = [n.id for n in nodes]
    if node_ids:
        from sqlalchemy import func
        relations_result = await db.execute(
            select(func.count()).where(
                KnowledgeRelation.source_id.in_(node_ids)
            )
        )
        relation_count = relations_result.scalar()
    else:
        relation_count = 0

    return {
        "total_nodes": len(nodes),
        "total_relations": relation_count,
        "nodes_by_type": type_counts
    }
