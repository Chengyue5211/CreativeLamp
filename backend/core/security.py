"""
绘创前程 — 安全模块
JWT认证 + bcrypt密码哈希 + Token黑名单 + 速率限制
"""
import os
import uuid
import time
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional
from collections import defaultdict

import jwt
import bcrypt
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.config import IS_PROD

# 配置
SECRET_KEY = os.getenv("HC_SECRET_KEY", "")
if not SECRET_KEY:
    if IS_PROD:
        raise RuntimeError("生产环境必须设置 HC_SECRET_KEY 环境变量")
    SECRET_KEY = "huichuang-dev-secret-key-only-for-dev"

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
ISSUER = "huichuang-qiancheng"
AUDIENCE = "huichuang-app"

security_scheme = HTTPBearer(auto_error=False)

# ============================================================
# Token黑名单（内存实现，生产应用Redis）
# ============================================================
_token_blacklist: set[str] = set()
_blacklist_expiry: dict[str, float] = {}


def blacklist_token(jti: str, exp_timestamp: float):
    """将token加入黑名单"""
    _token_blacklist.add(jti)
    _blacklist_expiry[jti] = exp_timestamp


def is_token_blacklisted(jti: str) -> bool:
    """检查token是否已被撤销"""
    # 清理过期条目
    now = time.time()
    expired = [k for k, v in _blacklist_expiry.items() if v < now]
    for k in expired:
        _token_blacklist.discard(k)
        _blacklist_expiry.pop(k, None)
    return jti in _token_blacklist


# ============================================================
# 速率限制（内存实现）
# ============================================================
_rate_limits: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # 秒
RATE_LIMIT_MAX_LOGIN = 10  # 每分钟最多10次登录尝试
RATE_LIMIT_MAX_REGISTER = 5  # 每分钟最多5次注册


def check_rate_limit(key: str, max_attempts: int = RATE_LIMIT_MAX_LOGIN):
    """检查速率限制"""
    now = time.time()
    attempts = _rate_limits[key]
    # 清理窗口外的记录
    _rate_limits[key] = [t for t in attempts if now - t < RATE_LIMIT_WINDOW]
    if len(_rate_limits[key]) >= max_attempts:
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")
    _rate_limits[key].append(now)


# ============================================================
# 密码
# ============================================================
def hash_password(password: str) -> str:
    """bcrypt 哈希密码"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ============================================================
# JWT
# ============================================================
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
        payload = jwt.decode(
            token, SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=ISSUER,
            audience=AUDIENCE,
        )
        # 检查黑名单
        jti = payload.get("jti")
        if jti and is_token_blacklisted(jti):
            raise HTTPException(status_code=401, detail="令牌已失效")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="令牌已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效令牌")


def extract_token_claims(token: str) -> Optional[dict]:
    """提取token中的claims（不验证签名，用于登出时获取jti/exp）"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],
                         issuer=ISSUER, audience=AUDIENCE)
    except jwt.InvalidTokenError:
        return None


# ============================================================
# FastAPI 依赖
# ============================================================
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
        "jti": payload.get("jti"),
        "exp": payload.get("exp"),
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
