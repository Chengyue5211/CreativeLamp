"""
作品系统路由 — 上传/列表/详情
"""
import os
import uuid
import shutil
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse

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

        # 写入元数据
        conn.execute(
            """INSERT INTO work_metadata (work_id, module) VALUES (?, ?)""",
            (work_id, None),
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
    child_id = current_user["user_id"]

    with get_db() as conn:
        work = conn.execute(
            """SELECT w.*, wm.prototype_tags_json, wm.transform_tags_json,
                      wm.increase_types_json, wm.series_name, wm.module
               FROM works w
               LEFT JOIN work_metadata wm ON w.id = wm.work_id
               WHERE w.id = ? AND w.child_id = ?""",
            (work_id, child_id),
        ).fetchone()

    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")

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
        "ai_score_originality": work["ai_score_originality"],
        "ai_score_detail": work["ai_score_detail"],
        "ai_feedback": work["ai_feedback"],
    }
