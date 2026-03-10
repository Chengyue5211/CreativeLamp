"""
家长系统路由 — 仪表盘/作品管理/成长报告
"""
from fastapi import APIRouter, Depends, HTTPException

from core.database import get_db
from core.security import require_parent

router = APIRouter()


@router.get("/dashboard")
async def parent_dashboard(
    current_user: dict = Depends(require_parent),
):
    """家长仪表盘 — 所有孩子的汇总数据"""
    parent_id = current_user["user_id"]

    with get_db() as conn:
        # 获取所有绑定的孩子
        children = conn.execute(
            """SELECT u.id, u.nickname, u.age, u.gender, u.level_grade, u.created_at
               FROM users u
               JOIN user_relations ur ON u.id = ur.child_id
               WHERE ur.parent_id = ? AND ur.is_active = 1 AND u.role = 'child'""",
            (parent_id,),
        ).fetchall()

        children_data = []
        for child in children:
            child_id = child["id"]

            # 每个孩子的统计
            total_works = conn.execute(
                "SELECT COUNT(*) as cnt FROM works WHERE child_id = ?",
                (child_id,),
            ).fetchone()["cnt"]

            total_tasks = conn.execute(
                "SELECT COUNT(*) as cnt FROM tasks WHERE child_id = ?",
                (child_id,),
            ).fetchone()["cnt"]

            completed_tasks = conn.execute(
                "SELECT COUNT(*) as cnt FROM tasks WHERE child_id = ? AND status IN ('submitted', 'evaluated')",
                (child_id,),
            ).fetchone()["cnt"]

            # 最新作品
            latest_work = conn.execute(
                "SELECT id, title, thumbnail_path, created_at FROM works WHERE child_id = ? ORDER BY created_at DESC LIMIT 1",
                (child_id,),
            ).fetchone()

            children_data.append({
                "id": child["id"],
                "nickname": child["nickname"],
                "age": child["age"],
                "gender": child["gender"],
                "level_grade": child["level_grade"],
                "joined_at": child["created_at"],
                "stats": {
                    "total_works": total_works,
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                },
                "latest_work": {
                    "id": latest_work["id"],
                    "title": latest_work["title"],
                    "thumbnail_path": latest_work["thumbnail_path"],
                    "created_at": latest_work["created_at"],
                } if latest_work else None,
            })

    return {
        "children": children_data,
        "total_children": len(children_data),
    }


@router.get("/child/{child_id}/works")
async def get_child_works(
    child_id: int,
    current_user: dict = Depends(require_parent),
):
    """获取指定孩子的所有作品"""
    parent_id = current_user["user_id"]

    with get_db() as conn:
        # 验证亲子关系
        relation = conn.execute(
            "SELECT id FROM user_relations WHERE parent_id = ? AND child_id = ? AND is_active = 1",
            (parent_id, child_id),
        ).fetchone()
        if not relation:
            raise HTTPException(status_code=403, detail="无权查看该孩子的作品")

        works = conn.execute(
            """SELECT w.id, w.title, w.description, w.image_path, w.thumbnail_path,
                      w.source_type, w.visibility, w.merch_candidate, w.evidence_candidate,
                      w.ai_score_originality, w.ai_feedback, w.created_at
               FROM works w
               WHERE w.child_id = ?
               ORDER BY w.created_at DESC""",
            (child_id,),
        ).fetchall()

    return {
        "works": [
            {
                "id": w["id"],
                "title": w["title"],
                "description": w["description"],
                "image_path": w["image_path"],
                "thumbnail_path": w["thumbnail_path"] or w["image_path"],
                "source_type": w["source_type"],
                "visibility": w["visibility"],
                "merch_candidate": bool(w["merch_candidate"]),
                "evidence_candidate": bool(w["evidence_candidate"]),
                "ai_score": w["ai_score_originality"],
                "ai_feedback": w["ai_feedback"],
                "created_at": w["created_at"],
            }
            for w in works
        ],
        "total": len(works),
    }


@router.put("/work/{work_id}/visibility")
async def update_work_visibility(
    work_id: int,
    visibility: str,
    current_user: dict = Depends(require_parent),
):
    """更新作品可见性"""
    parent_id = current_user["user_id"]

    if visibility not in ("private", "family", "public"):
        raise HTTPException(status_code=400, detail="无效的可见性级别")

    with get_db() as conn:
        # 验证家长对该作品的权限
        work = conn.execute(
            """SELECT w.child_id FROM works w
               JOIN user_relations ur ON w.child_id = ur.child_id
               WHERE w.id = ? AND ur.parent_id = ? AND ur.is_active = 1""",
            (work_id, parent_id),
        ).fetchone()

        if not work:
            raise HTTPException(status_code=403, detail="无权修改该作品")

        conn.execute(
            "UPDATE works SET visibility = ?, updated_at = datetime('now') WHERE id = ?",
            (visibility, work_id),
        )

    return {"work_id": work_id, "visibility": visibility}


@router.put("/work/{work_id}/candidate")
async def update_work_candidate(
    work_id: int,
    merch: bool = False,
    evidence: bool = False,
    rights: bool = False,
    current_user: dict = Depends(require_parent),
):
    """更新作品候选状态（文创/存证/确权）"""
    parent_id = current_user["user_id"]

    with get_db() as conn:
        work = conn.execute(
            """SELECT w.child_id FROM works w
               JOIN user_relations ur ON w.child_id = ur.child_id
               WHERE w.id = ? AND ur.parent_id = ? AND ur.is_active = 1""",
            (work_id, parent_id),
        ).fetchone()

        if not work:
            raise HTTPException(status_code=403, detail="无权修改该作品")

        conn.execute(
            """UPDATE works SET merch_candidate = ?, evidence_candidate = ?,
               rights_candidate = ?, updated_at = datetime('now') WHERE id = ?""",
            (int(merch), int(evidence), int(rights), work_id),
        )

    return {
        "work_id": work_id,
        "merch_candidate": merch,
        "evidence_candidate": evidence,
        "rights_candidate": rights,
    }
