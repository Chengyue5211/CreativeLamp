"""展示系统路由 — 展馆/成长档案"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/gallery/{child_id}")
async def get_gallery(child_id: int):
    """获取个人展馆"""
    return {"message": "待实现"}


@router.get("/growth/{child_id}")
async def get_growth_archive(child_id: int):
    """获取成长档案"""
    return {"message": "待实现"}
