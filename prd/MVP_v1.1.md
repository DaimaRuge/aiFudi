# SkyOne Shuge v1.1 - 用户认证与高级搜索

**版本**: v1.1
**日期**: 2026-02-03
**状态**: 开发中

---

## v1.1 新增功能

### 1. 用户认证系统

```python
# api/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from ..core.auth import AuthService, get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """用户注册"""
    # 检查邮箱是否已存在
    # 创建用户
    # 生成 token
    pass


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """用户登录"""
    # 验证邮箱密码
    # 生成 token
    pass


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """刷新令牌"""
    # 验证 refresh token
    # 生成新的 access token
    pass


@router.get("/me")
async def get_current_user_info(user_id: str = Depends(get_current_user)):
    """获取当前用户信息"""
    pass


@router.post("/logout")
async def logout():
    """退出登录"""
    pass
```

### 2. 用户模型

```python
# models/user.py

from sqlalchemy import Column, String, DateTime, Boolean
from ..core.database import Base
import uuid


class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    avatar = Column(String(512))
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    last_login_at = Column(DateTime)
```

### 3. 高级搜索 API

```python
# api/routers/search.py (增强版)

from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class AdvancedSearchRequest(BaseModel):
    query: str
    filters: Optional[Dict] = None
    sort: Optional[Dict] = None
    page: int = 1
    limit: int = 20
    mode: str = "hybrid"  # keyword/semantic/hybrid


@router.post("/advanced")
async def advanced_search(request: AdvancedSearchRequest):
    """高级搜索"""
    
    # 关键词搜索
    keyword_results = await _keyword_search(
        query=request.query,
        filters=request.filters,
        limit=request.limit * 2
    )
    
    # 语义搜索
    semantic_results = await _semantic_search(
        query=request.query,
        filters=request.filters,
        limit=request.limit * 2
    )
    
    # 混合排序
    results = _hybrid_ranking(
        keyword_results,
        semantic_results,
        query=request.query
    )
    
    return {
        "results": results[request.limit],
        "total": len(results),
        "mode": request.mode,
        "took": time.time() - start_time
    }


@router.post("/filters")
async def get_filter_options():
    """获取搜索筛选选项"""
    return {
        "categories": await _get_category_options(),
        "tags": await _get_tag_options(),
        "date_ranges": [
            {"label": "今天", "value": "today"},
            {"label": "本周", "value": "this_week"},
            {"label": "本月", "value": "this_month"},
            {"label": "今年", "value": "this_year"},
        ],
        "file_types": [
            {"label": "PDF", "value": ".pdf"},
            {"label": "Word", "value": ".docx"},
            {"label": "Excel", "value": ".xlsx"},
            {"label": "PPT", "value": ".pptx"},
            {"label": "Markdown", "value": ".md"},
        ]
    }
```

### 4. 批量操作 API

```python
# api/routers/documents.py (增强版)

from pydantic import BaseModel
from typing import List

class BatchOperationRequest(BaseModel):
    document_ids: List[str]
    operation: str  # move/classify/tag/delete


@router.post("/batch")
async def batch_operation(request: BatchOperationRequest):
    """批量操作文档"""
    
    results = {
        "succeeded": 0,
        "failed": 0,
        "errors": []
    }
    
    for doc_id in request.document_ids:
        try:
            if request.operation == "delete":
                await _delete_document(doc_id)
            elif request.operation == "classify":
                await _classify_document(doc_id)
            # ...
            results["succeeded"] += 1
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "document_id": doc_id,
                "error": str(e)
            })
    
    return results
```

### 5. 导入导出 API

```python
# api/routers/import_export.py

from fastapi import UploadFile, File
import zipfile
import json
import csv


@router.post("/import")
async def import_documents(
    file: UploadFile = File(...),
    format: str = "auto",  # auto/json/csv/zip
    strategy: str = "merge"  # merge/replace
):
    """导入文档"""
    
    if format == "zip":
        # 解压 ZIP 文件
        # 解析每个文件
        pass
    elif format == "json":
        # 解析 JSON 格式
        pass
    elif format == "csv":
        # 解析 CSV 格式
        pass
    
    return {
        "imported": 10,
        "skipped": 2,
        "errors": []
    }


@router.get("/export")
async def export_documents(
    format: str = "json",
    scope: str = "all",  # all/category/project
    category_id: str = None
):
    """导出文档"""
    
    # 获取文档数据
    # 导出为指定格式
    # 返回下载链接
    
    return {
        "download_url": "/api/v1/export/download/xxx",
        "expires_at": "2024-01-16T00:00:00Z",
        "file_size": 1024000
    }


@router.get("/export/download/{file_id}")
async def download_export(file_id: str):
    """下载导出文件"""
    pass
```

---

## 数据库迁移

```python
# alembic/versions/v1_1_user_auth.py

def upgrade():
    # 创建用户表
    op.create_table(
        'users',
        Column('id', String(36), primary_key=True),
        Column('email', String(255), unique=True, nullable=False),
        Column('password_hash', String(255), nullable=False),
        Column('name', String(100)),
        # ...
    )
    
    # 添加用户 ID 到文档表
    op.add_column('documents', Column('user_id', String(36)))


def downgrade():
    op.drop_table('users')
    op.drop_column('documents', 'user_id')
```

---

## 下一步

- [ ] 集成测试
- [ ] API 文档更新
- [ ] 前端认证界面
- [ ] 性能测试

---

**版本**: v1.1
**日期**: 2026-02-03
