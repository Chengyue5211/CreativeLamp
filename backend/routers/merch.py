"""文创系统路由 — 专属文创定制（待实现）"""
from fastapi import APIRouter, Depends, HTTPException

from core.security import get_current_user, require_parent

router = APIRouter()


@router.get("/types")
async def list_merch_types():
    """获取文创产品类型"""
    return {"merch_types": [], "message": "功能开发中", "total": 0}


@router.post("/preview")
async def create_merch_preview(user: dict = Depends(require_parent)):
    """生成文创预览效果图"""
    raise HTTPException(status_code=501, detail="功能开发中")


@router.post("/order")
async def create_order(user: dict = Depends(require_parent)):
    """创建文创订单"""
    raise HTTPException(status_code=501, detail="功能开发中")
