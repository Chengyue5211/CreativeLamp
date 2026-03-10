"""家长系统路由 — 作品管理/成长报告"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/dashboard")
async def parent_dashboard():
    """家长仪表盘"""
    return {"message": "待实现"}


@router.get("/children")
async def list_children():
    """获取绑定的孩子列表"""
    return {"message": "待实现"}
