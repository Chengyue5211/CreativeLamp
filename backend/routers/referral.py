"""推广系统路由 — 邀请/奖励"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/my-code")
async def get_my_invite_code():
    """获取我的邀请码"""
    return {"message": "待实现"}


@router.get("/rewards")
async def list_rewards():
    """获取奖励记录"""
    return {"message": "待实现"}
