"""认证路由 — 注册/登录/孩子管理"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from core.security import get_current_user, require_parent
from services.auth_service import register_parent, login, add_child, get_children, switch_to_child

router = APIRouter()


class RegisterRequest(BaseModel):
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")
    password: str = Field(..., min_length=6, max_length=32)
    nickname: str = ""


class LoginRequest(BaseModel):
    phone: str
    password: str


class AddChildRequest(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=20)
    age: int = Field(..., ge=2, le=18)
    gender: str = Field(default="unknown", pattern=r"^(male|female|unknown)$")


@router.post("/register")
async def api_register(req: RegisterRequest):
    """家长注册"""
    try:
        return register_parent(req.phone, req.password, req.nickname)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def api_login(req: LoginRequest):
    """登录"""
    try:
        return login(req.phone, req.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/children")
async def api_add_child(req: AddChildRequest, user: dict = Depends(require_parent)):
    """添加孩子"""
    try:
        return add_child(user["user_id"], req.nickname, req.age, req.gender)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/children")
async def api_get_children(user: dict = Depends(require_parent)):
    """获取孩子列表"""
    return {"children": get_children(user["user_id"])}


@router.post("/switch-child/{child_id}")
async def api_switch_child(child_id: int, user: dict = Depends(require_parent)):
    """切换到孩子模式"""
    try:
        return switch_to_child(user["user_id"], child_id)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/me")
async def api_get_me(user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    from core.database import get_db
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, role, nickname, age, gender, level_grade, avatar_url, created_at FROM users WHERE id = ?",
            (user["user_id"],)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="用户不存在")
    return dict(row)
