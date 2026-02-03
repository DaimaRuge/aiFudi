"""
天一阁 - 健康检查路由
"""

from fastapi import APIRouter
from ..core.config import settings
from sqlalchemy import text
from ..core.database import SYNC_ENGINE
from .schemas import HealthResponse

router = APIRouter(tags=["健康"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    
    # 检查数据库
    db_status = "connected"
    try:
        with SYNC_ENGINE.connect() as conn:
            conn.execute(text("SELECT 1"))
    except:
        db_status = "disconnected"
    
    return HealthResponse(
        status="healthy" if db_status == "connected" else "unhealthy",
        version=settings.APP_VERSION,
        name=settings.APP_NAME,
        database=db_status
    )


@router.get("/ready")
async def readiness_check():
    """就绪检查"""
    return {"status": "ready"}
