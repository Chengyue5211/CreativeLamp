"""文创系统路由 — 专属文创定制"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/types")
async def list_merch_types():
    """获取文创产品类型"""
    return {"message": "待实现"}


@router.post("/preview")
async def create_merch_preview():
    """生成文创预览效果图"""
    return {"message": "待实现"}


@router.post("/order")
async def create_order():
    """创建文创订单"""
    return {"message": "待实现"}
