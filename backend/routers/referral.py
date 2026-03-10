"""推广系统路由 — 邀请/奖励（待实现）"""
from fastapi import APIRouter, Depends, HTTPException

from core.security import get_current_user

router = APIRouter()


@router.get("/my-code")
async def get_my_invite_code(user: dict = Depends(get_current_user)):
    """获取我的邀请码"""
    return {"invite_code": None, "message": "功能开发中"}


@router.get("/rewards")
async def list_rewards(user: dict = Depends(get_current_user)):
    """获取奖励记录"""
    return {"rewards": [], "message": "功能开发中", "total": 0}
