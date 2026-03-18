"""推广系统路由 — 邀请码 / 推广仪表盘 / 奖励记录"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from core.security import get_current_user, require_parent
from services.referral_service import (
    ensure_invite_code,
    validate_invite_code,
    get_referral_dashboard,
    get_referral_list,
    get_reward_history,
    get_credit_balance,
)

router = APIRouter()


# ── 邀请码 ──────────────────────────────────────────────

@router.get("/my-code")
async def get_my_invite_code(user: dict = Depends(require_parent)):
    """获取我的邀请码"""
    code = ensure_invite_code(user["user_id"])
    return {"invite_code": code}


class ValidateCodeRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)


@router.post("/validate-code")
async def api_validate_code(req: ValidateCodeRequest):
    """验证邀请码（注册前调用，无需登录）"""
    result = validate_invite_code(req.code)
    if result:
        return {"valid": True, "inviter_nickname": result["nickname"]}
    return {"valid": False}


# ── 推广仪表盘 ──────────────────────────────────────────

@router.get("/dashboard")
async def api_dashboard(user: dict = Depends(require_parent)):
    """获取推广数据仪表盘"""
    return get_referral_dashboard(user["user_id"])


# ── 推荐记录 ────────────────────────────────────────────

@router.get("/referrals")
async def api_referral_list(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    user: dict = Depends(require_parent),
):
    """获取我的推荐记录"""
    return get_referral_list(user["user_id"], page, limit)


# ── 学币 ────────────────────────────────────────────────

@router.get("/balance")
async def api_balance(user: dict = Depends(require_parent)):
    """获取学币余额"""
    return {"credit_balance": get_credit_balance(user["user_id"])}


@router.get("/rewards")
async def api_rewards(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    user: dict = Depends(require_parent),
):
    """获取学币流水"""
    return get_reward_history(user["user_id"], page, limit)
