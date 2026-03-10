"""
绘创前程 — 安全模块
JWT认证 + bcrypt密码哈希
"""
import os
import uuid
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
import bcrypt
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# 配置
SECRET_KEY = os.getenv("HC_SECRET_KEY", "huichuang-dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
ISSUER = "huichuang-qiancheng"
AUDIENCE = "huichuang-app"

security_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """bcrypt 哈希密码"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: int, role: str, extra: Optional[dict] = None) -> str:
    """创建JWT访问令牌"""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iss": ISSUER,
        "aud": AUDIENCE,
        "iat": now,
        "exp": now + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
        "jti": str(uuid.uuid4()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """解码并验证JWT"""
    try:
        return jwt.decode(
            token, SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=ISSUER,
            audience=AUDIENCE,
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="令牌已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效令牌")


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> dict:
    """获取当前认证用户"""
    if not credentials:
        raise HTTPException(status_code=401, detail="未提供认证信息")
    payload = decode_token(credentials.credentials)
    return {
        "user_id": int(payload["sub"]),
        "role": payload["role"],
    }


async def require_parent(current_user: dict = Depends(get_current_user)) -> dict:
    """要求家长角色"""
    if current_user["role"] not in ("parent", "admin"):
        raise HTTPException(status_code=403, detail="需要家长权限")
    return current_user


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """要求管理员角色"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user
