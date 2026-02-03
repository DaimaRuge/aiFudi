"""
天一阁 - 分类路由
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from ..core.database import get_async_db
from ..models import Category
from .schemas import CategoryResponse, CategoryCreate

router = APIRouter(prefix="/categories", tags=["分类"])


@router.get("")
async def list_categories(
    parent_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """获取分类列表"""
    
    query = select(Category)
    
    if parent_id:
        query = query.where(Category.parent_id == parent_id)
    
    query = query.order_by(Category.sort_order, Category.name)
    
    result = await db.execute(query)
    categories = result.scalars().all()
    
    return {
        "success": True,
        "data": [CategoryResponse.model_validate(cat) for cat in categories]
    }


@router.get("/tree")
async def get_category_tree(db: AsyncSession = Depends(get_async_db)):
    """获取分类树"""
    
    result = await db.execute(select(Category))
    all_categories = result.scalars().all()
    
    def build_tree(parent_id: Optional[str] = None) -> List[dict]:
        children = []
        for cat in all_categories:
            if cat.parent_id == parent_id:
                children.append({
                    **CategoryResponse.model_validate(cat).model_dump(),
                    "children": build_tree(cat.id)
                })
        return children
    
    tree = build_tree()
    
    return {"success": True, "data": tree}


@router.get("/{cat_id}", response_model=CategoryResponse)
async def get_category(cat_id: str, db: AsyncSession = Depends(get_async_db)):
    """获取分类详情"""
    
    result = await db.execute(
        select(Category).where(Category.id == cat_id)
    )
    cat = result.scalar_one_or_none()
    
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    return CategoryResponse.model_validate(cat)


@router.post("")
async def create_category(
    request: CategoryCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """创建分类"""
    
    import uuid
    
    # 构建路径
    if request.parent_id:
        parent_result = await db.execute(
            select(Category).where(Category.id == request.parent_id)
        )
        parent = parent_result.scalar_one_or_none()
        
        if not parent:
            raise HTTPException(status_code=404, detail="父分类不存在")
        
        path = f"{parent.path}/{request.name}"
    else:
        path = f"/{request.name}"
    
    # 检查路径是否存在
    existing = await db.execute(
        select(Category).where(Category.path == path)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="分类路径已存在")
    
    category = Category(
        id=str(uuid.uuid4()),
        name=request.name,
        parent_id=request.parent_id,
        path=path,
        type=request.type,
        color=request.color
    )
    
    db.add(category)
    await db.commit()
    
    return {"success": True, "data": CategoryResponse.model_validate(category)}


@router.delete("/{cat_id}")
async def delete_category(cat_id: str, db: AsyncSession = Depends(get_async_db)):
    """删除分类"""
    
    result = await db.execute(
        select(Category).where(Category.id == cat_id)
    )
    cat = result.scalar_one_or_none()
    
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 检查是否有子分类
    children = await db.execute(
        select(Category).where(Category.parent_id == cat_id)
    )
    if children.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="请先删除子分类")
    
    await db.delete(cat)
    await db.commit()
    
    return {"success": True, "message": "删除成功"}
