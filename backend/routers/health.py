"""健康检查端点"""
from fastapi import APIRouter

router = APIRouter(tags=["系统"])


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "绘创前程"}
