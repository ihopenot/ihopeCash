"""
认证模块 - JWT Token 生成和验证
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import sys
import os

# 添加父目录到 path 以便导入 config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

# HTTP Bearer 认证方案
security = HTTPBearer()


def verify_password(password: str, config: Config) -> bool:
    """验证密码是否匹配配置
    
    Args:
        password: 用户输入的密码
        config: Config 实例
        
    Returns:
        是否匹配
    """
    return password == config.web_password


def create_jwt_token(config: Config) -> dict:
    """生成 JWT token
    
    Args:
        config: Config 实例
        
    Returns:
        包含 token 和过期时间的字典
    """
    # 计算过期时间
    expire_at = datetime.utcnow() + timedelta(days=config.token_expire_days)
    
    # Token payload
    payload = {
        "exp": expire_at,
        "iat": datetime.utcnow(),
        "sub": "web_user"  # 单用户场景，固定为 web_user
    }
    
    # 生成 token
    token = jwt.encode(payload, config.jwt_secret, algorithm="HS256")
    
    return {
        "token": token,
        "expire_at": expire_at.isoformat() + "Z"
    }


def verify_jwt_token(token: str, config: Config) -> dict:
    """验证 JWT token
    
    Args:
        token: JWT token 字符串
        config: Config 实例
        
    Returns:
        解码后的 payload
        
    Raises:
        jwt.ExpiredSignatureError: Token 已过期
        jwt.InvalidTokenError: Token 无效
    """
    try:
        payload = jwt.decode(token, config.jwt_secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 已过期"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效"
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """FastAPI 依赖注入 - 验证当前用户
    
    从 Authorization header 中提取 token 并验证
    
    Args:
        credentials: HTTP Bearer 凭证
        
    Returns:
        用户信息（payload）
        
    Raises:
        HTTPException: 认证失败
    """
    # 加载配置
    config = Config()
    
    # 验证 token
    try:
        payload = verify_jwt_token(credentials.credentials, config)
        return payload
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"认证失败: {str(e)}"
        )


def verify_ws_token(token: str) -> dict:
    """验证 WebSocket 连接的 token（从查询参数）
    
    Args:
        token: JWT token 字符串
        
    Returns:
        解码后的 payload
        
    Raises:
        HTTPException: 认证失败
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少 token"
        )
    
    config = Config()
    return verify_jwt_token(token, config)
