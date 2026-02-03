"""
天一阁 - 认证路由
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import EmailStr
from typing import Optional
from datetime import datetime
from ..core.database import get_async_db
from ..models import User
from .schemas import TokenResponse, LoginRequest, RegisterRequest
from ..core.auth import AuthService
from passlib.context import CryptContext
import uuid

router = APIRouter(prefix="/auth", tags=["认证"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
auth_service = AuthService()


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_async_db)):
    """用户注册"""
    
    # 检查邮箱
    existing = await db.execute(
        select(User).where(User.email == request.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    
    # 创建用户
    user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        password_hash=pwd_context.hash(request.password),
        name=request.name
    )
    
    db.add(user)
    await db.commit()
    
    # 生成 token
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_async_db)):
    """用户登录"""
    
    # 查找用户
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    
    # 验证密码
    if not pwd_context.verify(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账户已被禁用")
    
    # 更新登录时间
    user.last_login_at = datetime.utcnow()
    await db.commit()
    
    # 生成 token
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """刷新令牌"""
    
    user_id = auth_service.validate_refresh_token(refresh_token)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="无效的刷新令牌")
    
    new_access_token = auth_service.create_access_token(user_id)
    new_refresh_token = auth_service.create_refresh_token(user_id)
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )
