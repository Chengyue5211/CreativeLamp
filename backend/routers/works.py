"""作品系统路由 — 上传/AI评估/管理"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/upload")
async def upload_work():
    """上传作品（拍照）"""
    return {"message": "待实现"}


@router.get("/my")
async def list_my_works():
    """获取我的作品列表"""
    return {"message": "待实现"}
