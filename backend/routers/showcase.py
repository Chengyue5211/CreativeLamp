"""
展示系统路由 — 展馆/成长档案/进展追踪/成长报告
"""
import json
from fastapi import APIRouter, Depends, HTTPException

from core.database import get_db
from core.security import get_current_user

router = APIRouter()


@router.get("/growth")
async def get_growth_archive(
    current_user: dict = Depends(get_current_user),
):
    """获取孩子的成长档案"""
    child_id = current_user["user_id"]

    with get_db() as conn:
        # 基本信息
        child = conn.execute(
            "SELECT nickname, age, level_grade, created_at FROM users WHERE id = ?",
            (child_id,),
        ).fetchone()

        if not child:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 统计数据
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

        in_progress_tasks = conn.execute(
            "SELECT COUNT(*) as cnt FROM tasks WHERE child_id = ? AND status = 'in_progress'",
            (child_id,),
        ).fetchone()["cnt"]

        # 按模块统计
        module_a_tasks = conn.execute(
            """SELECT COUNT(*) as cnt FROM tasks t
               JOIN task_templates tt ON t.template_id = tt.id
               WHERE t.child_id = ? AND tt.module = 'A'""",
            (child_id,),
        ).fetchone()["cnt"]

        module_b_tasks = conn.execute(
            """SELECT COUNT(*) as cnt FROM tasks t
               JOIN task_templates tt ON t.template_id = tt.id
               WHERE t.child_id = ? AND tt.module = 'B'""",
            (child_id,),
        ).fetchone()["cnt"]

        # 最近作品
        recent_works = conn.execute(
            """SELECT id, title, image_path, thumbnail_path, created_at, source_type
               FROM works WHERE child_id = ?
               ORDER BY created_at DESC LIMIT 6""",
            (child_id,),
        ).fetchall()

        # 按月统计作品数
        monthly_works = conn.execute(
            """SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as cnt
               FROM works WHERE child_id = ?
               GROUP BY month ORDER BY month DESC LIMIT 12""",
            (child_id,),
        ).fetchall()

        # 评价维度平均分（已评价的作品）
        eval_avg = conn.execute(
            """SELECT
               COUNT(*) as evaluated_count,
               AVG(ai_score_originality) as avg_originality,
               AVG(ai_score_detail) as avg_detail,
               AVG(ai_score_composition) as avg_composition,
               AVG(ai_score_expression) as avg_expression
               FROM works
               WHERE child_id = ? AND ai_score_originality IS NOT NULL""",
            (child_id,),
        ).fetchone()

        # 最佳作品（综合分最高）
        best_work = conn.execute(
            """SELECT id, title, thumbnail_path, image_path,
                      (ai_score_originality + ai_score_detail + ai_score_composition + ai_score_expression) / 4.0 as avg_score
               FROM works
               WHERE child_id = ? AND ai_score_originality IS NOT NULL
               ORDER BY avg_score DESC LIMIT 1""",
            (child_id,),
        ).fetchone()

        # 最近评价趋势（最近5件已评价作品的分数）
        eval_trend = conn.execute(
            """SELECT id, title,
                      ai_score_originality, ai_score_detail,
                      ai_score_composition, ai_score_expression,
                      ai_evaluated_at
               FROM works
               WHERE child_id = ? AND ai_score_originality IS NOT NULL
               ORDER BY ai_evaluated_at DESC LIMIT 5""",
            (child_id,),
        ).fetchall()

    evaluated_count = eval_avg["evaluated_count"] if eval_avg else 0

    return {
        "child": {
            "nickname": child["nickname"],
            "age": child["age"],
            "level_grade": child["level_grade"],
            "joined_at": child["created_at"],
        },
        "stats": {
            "total_works": total_works,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "module_a_tasks": module_a_tasks,
            "module_b_tasks": module_b_tasks,
            "evaluated_works": evaluated_count,
        },
        "ability_radar": {
            "originality": round(eval_avg["avg_originality"] or 0, 1),
            "detail": round(eval_avg["avg_detail"] or 0, 1),
            "composition": round(eval_avg["avg_composition"] or 0, 1),
            "expression": round(eval_avg["avg_expression"] or 0, 1),
        } if evaluated_count > 0 else None,
        "best_work": {
            "id": best_work["id"],
            "title": best_work["title"],
            "thumbnail_path": best_work["thumbnail_path"] or best_work["image_path"],
            "avg_score": round(best_work["avg_score"], 1),
        } if best_work else None,
        "eval_trend": [
            {
                "id": e["id"],
                "title": e["title"],
                "scores": {
                    "originality": e["ai_score_originality"],
                    "detail": e["ai_score_detail"],
                    "composition": e["ai_score_composition"],
                    "expression": e["ai_score_expression"],
                },
                "evaluated_at": e["ai_evaluated_at"],
            }
            for e in eval_trend
        ],
        "recent_works": [
            {
                "id": w["id"],
                "title": w["title"],
                "image_path": w["image_path"],
                "thumbnail_path": w["thumbnail_path"] or w["image_path"],
                "created_at": w["created_at"],
                "source_type": w["source_type"],
            }
            for w in recent_works
        ],
        "monthly_works": [
            {"month": m["month"], "count": m["cnt"]}
            for m in monthly_works
        ],
    }
