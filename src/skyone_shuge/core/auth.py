"""
天一阁 - 认证服务

JWT Token 管理
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from ..core.config import settings
import uuid


class AuthService:
    """认证服务"""
    
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = settings.ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def create_access_token(self, user_id: str, additional_claims: dict = None) -> str:
        """创建访问令牌"""
        
        expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "sub": user_id,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
    
    def create_refresh_token(self, user_id: str) -> str:
        """创建刷新令牌"""
        
        expire = datetime.utcnow() + timedelta(days=7)
        
        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": str(uuid.uuid4())
        }
        
        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
    
    def decode_token(self, token: str) -> dict:
        """解码令牌"""
        
        try:
            return jwt.decode(
                token,
                self.SECRET_KEY,
                algorithms=[self.ALGORITHM]
            )
        except JWTError as e:
            print(f"Token decode error: {e}")
            return None
    
    def validate_access_token(self, token: str) -> Optional[str]:
        """验证访问令牌"""
        
        payload = self.decode_token(token)
        
        if not payload:
            return None
        
        if payload.get("type") != "access":
            return None
        
        exp = payload.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            return None
        
        return payload.get("sub")
    
    def validate_refresh_token(self, token: str) -> Optional[str]:
        """验证刷新令牌"""
        
        payload = self.decode_token(token)
        
        if not payload:
            return None
        
        if payload.get("type") != "refresh":
            return None
        
        return payload.get("sub")
