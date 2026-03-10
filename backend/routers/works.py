"""
作品系统路由 — 上传/列表/详情/评价
"""
import json
import os
import uuid
import shutil
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from core.database import get_db
from core.security import get_current_user
from core.config import UPLOAD_DIR, THUMBNAIL_DIR, ALLOWED_IMAGE_TYPES, MAX_UPLOAD_SIZE_MB

router = APIRouter()


@router.post("/upload")
async def upload_work(
    image: UploadFile = File(...),
    title: str = Form("无题"),
    description: str = Form(""),
    contour_id: str = Form(""),
    task_id: int = Form(0),
    current_user: dict = Depends(get_current_user),
):
    """上传作品（拍照）"""
    child_id = current_user["user_id"]

    # 验证文件类型
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="只支持 JPG/PNG/WebP 图片格式")

    # 读取文件（检查大小）
    content = await image.read()
    if len(content) > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"图片大小不能超过 {MAX_UPLOAD_SIZE_MB}MB")

    # 生成唯一文件名
    ext = os.path.splitext(image.filename or "photo.jpg")[1] or ".jpg"
    filename = f"{child_id}_{uuid.uuid4().hex[:12]}{ext}"
    filepath = UPLOAD_DIR / filename

    # 保存文件
    with open(filepath, "wb") as f:
        f.write(content)

    # 缩略图路径（暂时用原图）
    thumb_path = f"/api/works/image/{filename}"
    image_path = f"/api/works/image/{filename}"

    # 确定来源类型
    source_type = "task" if task_id > 0 else "free_upload"

    # 写入数据库
    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO works (child_id, task_id, title, description, image_path, thumbnail_path, source_type, visibility)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                child_id,
                task_id if task_id > 0 else None,
                title[:100],
                description[:500],
                image_path,
                thumb_path,
                source_type,
                "private",
            ),
        )
        work_id = cursor.lastrowid

        # 写入元数据（从任务获取模块信息）
        module = None
        if task_id > 0:
            task_row = conn.execute(
                """SELECT tt.module FROM tasks t
                   JOIN task_templates tt ON t.template_id = tt.id
                   WHERE t.id = ? AND t.child_id = ?""",
                (task_id, child_id),
            ).fetchone()
            if task_row:
                module = task_row["module"]
                # 自动更新任务状态为submitted
                conn.execute(
                    "UPDATE tasks SET status = 'submitted', submitted_at = datetime('now') WHERE id = ? AND status IN ('assigned', 'in_progress')",
                    (task_id,),
                )

        conn.execute(
            """INSERT INTO work_metadata (work_id, module) VALUES (?, ?)""",
            (work_id, module),
        )

        # 如果指定了轮廓ID，记入元数据
        if contour_id:
            conn.execute(
                "UPDATE work_metadata SET prototype_tags_json = ? WHERE work_id = ?",
                (json.dumps([{"type": "contour", "id": contour_id}]), work_id),
            )

    return {
        "work_id": work_id,
        "title": title,
        "image_path": image_path,
        "message": "作品上传成功！",
    }


@router.get("/my")
async def list_my_works(
    current_user: dict = Depends(get_current_user),
):
    """获取我的作品列表"""
    child_id = current_user["user_id"]

    with get_db() as conn:
        rows = conn.execute(
            """SELECT id, title, description, image_path, thumbnail_path,
                      source_type, visibility, created_at
               FROM works
               WHERE child_id = ?
               ORDER BY created_at DESC""",
            (child_id,),
        ).fetchall()

    works = []
    for r in rows:
        works.append({
            "id": r["id"],
            "title": r["title"],
            "description": r["description"],
            "image_path": r["image_path"],
            "thumbnail_path": r["thumbnail_path"] or r["image_path"],
            "source_type": r["source_type"],
            "visibility": r["visibility"],
            "created_at": r["created_at"],
        })

    return {"works": works, "total": len(works)}


@router.get("/image/{filename}")
async def get_work_image(filename: str):
    """获取作品图片"""
    from fastapi.responses import FileResponse

    # 安全检查：防止路径遍历
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="非法文件名")

    filepath = UPLOAD_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="图片不存在")

    return FileResponse(str(filepath))


@router.get("/{work_id}")
async def get_work_detail(
    work_id: int,
    current_user: dict = Depends(get_current_user),
):
    """获取作品详情"""
    user_id = current_user["user_id"]
    role = current_user.get("role", "child")

    with get_db() as conn:
        if role == "parent":
            # 家长可以查看自己孩子的作品
            work = conn.execute(
                """SELECT w.*, wm.prototype_tags_json, wm.transform_tags_json,
                          wm.increase_types_json, wm.series_name, wm.module
                   FROM works w
                   LEFT JOIN work_metadata wm ON w.id = wm.work_id
                   JOIN user_relations ur ON w.child_id = ur.child_id
                   WHERE w.id = ? AND ur.parent_id = ? AND ur.is_active = 1""",
                (work_id, user_id),
            ).fetchone()
        else:
            work = conn.execute(
                """SELECT w.*, wm.prototype_tags_json, wm.transform_tags_json,
                          wm.increase_types_json, wm.series_name, wm.module
                   FROM works w
                   LEFT JOIN work_metadata wm ON w.id = wm.work_id
                   WHERE w.id = ? AND w.child_id = ?""",
                (work_id, user_id),
            ).fetchone()

    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")

    # 获取关联任务信息
    task_info = None
    if work["task_id"]:
        with get_db() as conn2:
            task = conn2.execute(
                """SELECT t.id, t.status, tt.title, tt.module, tt.task_type,
                          tt.instruction, tt.requirement_json
                   FROM tasks t
                   JOIN task_templates tt ON t.template_id = tt.id
                   WHERE t.id = ?""",
                (work["task_id"],),
            ).fetchone()
            if task:
                task_info = {
                    "id": task["id"],
                    "title": task["title"],
                    "module": task["module"],
                    "task_type": task["task_type"],
                    "instruction": task["instruction"],
                    "status": task["status"],
                }

    # 解析metadata JSON
    prototype_tags = []
    transform_tags = []
    increase_types = []
    try:
        if work["prototype_tags_json"]:
            prototype_tags = json.loads(work["prototype_tags_json"])
        if work["transform_tags_json"]:
            transform_tags = json.loads(work["transform_tags_json"])
        if work["increase_types_json"]:
            increase_types = json.loads(work["increase_types_json"])
    except (json.JSONDecodeError, TypeError):
        pass

    return {
        "id": work["id"],
        "title": work["title"],
        "description": work["description"],
        "image_path": work["image_path"],
        "thumbnail_path": work["thumbnail_path"],
        "source_type": work["source_type"],
        "visibility": work["visibility"],
        "created_at": work["created_at"],
        "module": work["module"],
        "series_name": work["series_name"],
        "prototype_tags": prototype_tags,
        "transform_tags": transform_tags,
        "increase_types": increase_types,
        "task": task_info,
        "evaluation": {
            "originality": work["ai_score_originality"],
            "detail": work["ai_score_detail"],
            "composition": work["ai_score_composition"],
            "expression": work["ai_score_expression"],
            "feedback": work["ai_feedback"],
            "evaluated_at": work["ai_evaluated_at"],
        } if work["ai_score_originality"] is not None else None,
    }


class EvaluationRequest(BaseModel):
    originality: float = Field(..., ge=0, le=10, description="原创性 0-10")
    detail: float = Field(..., ge=0, le=10, description="细节丰富度 0-10")
    composition: float = Field(..., ge=0, le=10, description="构图表现 0-10")
    expression: float = Field(..., ge=0, le=10, description="创意表达 0-10")
    feedback: str = Field("", max_length=500, description="文字评语")


@router.post("/{work_id}/evaluate")
async def evaluate_work(
    work_id: int,
    req: EvaluationRequest,
    current_user: dict = Depends(get_current_user),
):
    """评价作品（家长或孩子自评）"""
    user_id = current_user["user_id"]

    with get_db() as conn:
        # 验证权限：自己的作品 或 家长对孩子作品
        work = conn.execute(
            "SELECT child_id FROM works WHERE id = ?", (work_id,)
        ).fetchone()
        if not work:
            raise HTTPException(status_code=404, detail="作品不存在")

        child_id = work["child_id"]
        if child_id != user_id:
            # 检查是否为该孩子的家长
            rel = conn.execute(
                "SELECT id FROM user_relations WHERE parent_id = ? AND child_id = ? AND is_active = 1",
                (user_id, child_id),
            ).fetchone()
            if not rel:
                raise HTTPException(status_code=403, detail="无权评价该作品")

        conn.execute(
            """UPDATE works SET
               ai_score_originality = ?, ai_score_detail = ?,
               ai_score_composition = ?, ai_score_expression = ?,
               ai_feedback = ?, ai_evaluated_at = datetime('now'),
               updated_at = datetime('now')
               WHERE id = ?""",
            (req.originality, req.detail, req.composition, req.expression,
             req.feedback, work_id),
        )

        # 如果关联了任务，更新任务状态为 evaluated
        task_row = conn.execute(
            "SELECT task_id FROM works WHERE id = ?", (work_id,)
        ).fetchone()
        if task_row and task_row["task_id"]:
            conn.execute(
                "UPDATE tasks SET status = 'evaluated', evaluated_at = datetime('now') WHERE id = ? AND status = 'submitted'",
                (task_row["task_id"],),
            )

    avg_score = round((req.originality + req.detail + req.composition + req.expression) / 4, 1)

    return {
        "work_id": work_id,
        "scores": {
            "originality": req.originality,
            "detail": req.detail,
            "composition": req.composition,
            "expression": req.expression,
            "average": avg_score,
        },
        "feedback": req.feedback,
        "message": "评价成功！",
    }


@router.put("/{work_id}/edit")
async def edit_work(
    work_id: int,
    title: str = Form(None),
    description: str = Form(None),
    current_user: dict = Depends(get_current_user),
):
    """编辑作品标题和描述"""
    child_id = current_user["user_id"]

    with get_db() as conn:
        work = conn.execute(
            "SELECT id FROM works WHERE id = ? AND child_id = ?",
            (work_id, child_id),
        ).fetchone()
        if not work:
            raise HTTPException(status_code=404, detail="作品不存在")

        updates = []
        params = []
        if title is not None:
            updates.append("title = ?")
            params.append(title[:100])
        if description is not None:
            updates.append("description = ?")
            params.append(description[:500])

        if updates:
            updates.append("updated_at = datetime('now')")
            params.append(work_id)
            conn.execute(
                f"UPDATE works SET {', '.join(updates)} WHERE id = ?",
                tuple(params),
            )

    return {"work_id": work_id, "message": "修改成功"}
