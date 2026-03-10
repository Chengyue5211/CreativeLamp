"""训练系统路由 — 双训练核心"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from core.security import get_current_user
from services.training_service import (
    generate_daily_task, get_today_tasks, get_task_detail,
    update_task_status, get_prototype_library, get_transform_library,
    LEVEL_CONFIG, TASK_TYPE_INFO, CONTOUR_LIBRARY
)

router = APIRouter()


@router.get("/prototypes")
async def api_list_prototypes(
    module: Optional[str] = Query(None, pattern=r"^[AB]$"),
    category: Optional[str] = None,
):
    """获取原型库"""
    protos = get_prototype_library(module, category)
    return {"prototypes": protos, "total": len(protos)}


@router.get("/transforms")
async def api_list_transforms():
    """获取7种变形动作（图形变形与结构生成）"""
    transforms = get_transform_library()
    return {"actions": transforms, "total": len(transforms)}


@router.get("/increase-subtypes")
async def api_list_increase_subtypes():
    """获取增加动作的5种子类型"""
    from data.transforms import INCREASE_SUBTYPES
    return {"subtypes": INCREASE_SUBTYPES, "total": len(INCREASE_SUBTYPES)}


@router.get("/contours")
async def api_list_contours(
    category: Optional[str] = None,
):
    """获取轮廓图形库"""
    contours = CONTOUR_LIBRARY
    if category:
        contours = [c for c in contours if c["category"] == category]
    return {"contours": contours, "total": len(contours)}


@router.get("/levels")
async def api_list_levels():
    """获取九级体系说明"""
    return {
        "levels": [
            {"id": k, "name": v["name"], "age_range": v["age_range"]}
            for k, v in LEVEL_CONFIG.items()
        ]
    }


@router.get("/task-types")
async def api_list_task_types():
    """获取任务类型说明"""
    return {
        "task_types": [
            {"id": k, **v}
            for k, v in TASK_TYPE_INFO.items()
        ]
    }


@router.post("/daily-task")
async def api_generate_daily_task(user: dict = Depends(get_current_user)):
    """生成今日训练任务"""
    child_id = user["user_id"]
    if user["role"] == "parent":
        raise HTTPException(status_code=400, detail="请先切换到孩子模式")
    try:
        result = generate_daily_task(child_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/today")
async def api_get_today(user: dict = Depends(get_current_user)):
    """获取今日任务"""
    child_id = user["user_id"]
    result = get_today_tasks(child_id)
    if not result:
        return {"message": "今天还没有任务哦，点击开始训练吧！", "tasks": []}
    return result


@router.get("/task/{task_id}")
async def api_get_task(task_id: int, user: dict = Depends(get_current_user)):
    """获取任务详情（含完整原型/变形数据）"""
    try:
        return get_task_detail(task_id, user["user_id"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/task/{task_id}/status")
async def api_update_task_status(
    task_id: int,
    status: str = Query(..., pattern=r"^(in_progress|submitted|evaluated)$"),
    user: dict = Depends(get_current_user),
):
    """更新任务状态"""
    try:
        return update_task_status(task_id, user["user_id"], status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
