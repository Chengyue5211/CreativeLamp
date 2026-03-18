"""文创系统路由 — 专属文创定制 + 学币支付"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from core.security import require_parent
from core.database import get_db

router = APIRouter()


def _seed_merch_types(conn):
    """确保文创产品类型数据存在"""
    existing = conn.execute("SELECT COUNT(*) as cnt FROM merch_types").fetchone()["cnt"]
    if existing > 0:
        return
    types = [
        ("postcard", "明信片", "Postcard", "孩子画作印制成精美明信片", 500, 1),
        ("sticker", "贴纸套装", "Sticker Set", "作品变成趣味贴纸（6张/套）", 800, 2),
        ("photobook", "画册", "Photo Book", "精选作品集结成册，记录成长", 3500, 3),
        ("tshirt", "T恤", "T-Shirt", "穿上孩子的创意，独一无二", 4500, 4),
        ("mug", "马克杯", "Mug", "每天用孩子的画喝水", 3000, 5),
        ("canvas", "帆布画", "Canvas Print", "作品印制在画布上，挂在墙上", 6000, 6),
        ("tote_bag", "帆布包", "Tote Bag", "把创意背出门", 3500, 7),
    ]
    for t in types:
        conn.execute(
            """INSERT OR IGNORE INTO merch_types (id, name_zh, name_en, description, base_price, sort_order)
               VALUES (?, ?, ?, ?, ?, ?)""",
            t,
        )


@router.get("/types")
async def list_merch_types():
    """获取文创产品类型列表"""
    with get_db() as conn:
        _seed_merch_types(conn)
        rows = conn.execute(
            "SELECT id, name_zh, name_en, description, base_price, sort_order FROM merch_types WHERE is_available = 1 ORDER BY sort_order"
        ).fetchall()
    return {
        "merch_types": [
            {**dict(r), "price_display": f"¥{r['base_price'] / 100:.0f}" if r["base_price"] >= 100 else f"¥{r['base_price'] / 100:.2f}"}
            for r in rows
        ],
        "total": len(rows),
    }


class OrderRequest(BaseModel):
    merch_type_id: str = Field(..., min_length=1)
    work_ids: List[int] = Field(..., min_length=1, max_length=20)
    use_credits: int = Field(default=0, ge=0)
    shipping_address: str = Field(default="", max_length=200)


@router.post("/order")
async def create_order(req: OrderRequest, user: dict = Depends(require_parent)):
    """创建文创订单（支持学币抵扣）"""
    parent_id = user["user_id"]

    with get_db() as conn:
        _seed_merch_types(conn)

        # 查产品
        merch = conn.execute(
            "SELECT id, name_zh, base_price FROM merch_types WHERE id = ? AND is_available = 1",
            (req.merch_type_id,),
        ).fetchone()
        if not merch:
            raise HTTPException(status_code=404, detail="产品类型不存在")

        # 验证作品归属
        for wid in req.work_ids:
            work = conn.execute(
                """SELECT w.id FROM works w
                   JOIN user_relations ur ON ur.child_id = w.child_id
                   WHERE w.id = ? AND ur.parent_id = ?""",
                (wid, parent_id),
            ).fetchone()
            if not work:
                raise HTTPException(status_code=403, detail=f"作品 {wid} 不属于您的孩子")

        total_price = merch["base_price"]

        # 学币抵扣 (1学币 = 1分钱)
        credits_used = 0
        if req.use_credits > 0:
            balance = conn.execute(
                "SELECT COALESCE(credit_balance, 0) as bal FROM users WHERE id = ?",
                (parent_id,),
            ).fetchone()["bal"]

            credits_used = min(req.use_credits, balance, total_price)
            if credits_used > 0:
                conn.execute(
                    "UPDATE users SET credit_balance = credit_balance - ? WHERE id = ?",
                    (credits_used, parent_id),
                )
                new_bal = conn.execute(
                    "SELECT COALESCE(credit_balance, 0) as bal FROM users WHERE id = ?",
                    (parent_id,),
                ).fetchone()["bal"]
                conn.execute(
                    """INSERT INTO credit_transactions (user_id, amount, balance_after, tx_type, description)
                       VALUES (?, ?, ?, 'merch_purchase', ?)""",
                    (parent_id, -credits_used, new_bal, f"购买{merch['name_zh']}"),
                )

        # 获取孩子ID（取第一个作品的）
        child_row = conn.execute(
            "SELECT child_id FROM works WHERE id = ?", (req.work_ids[0],)
        ).fetchone()

        import json
        cursor = conn.execute(
            """INSERT INTO merch_orders (parent_id, child_id, merch_type_id, work_ids_json, status, total_price, shipping_address)
               VALUES (?, ?, ?, ?, 'confirmed', ?, ?)""",
            (parent_id, child_row["child_id"], req.merch_type_id,
             json.dumps(req.work_ids), total_price - credits_used, req.shipping_address),
        )
        order_id = cursor.lastrowid

    return {
        "order_id": order_id,
        "merch_type": merch["name_zh"],
        "total_price": total_price,
        "credits_used": credits_used,
        "amount_due": total_price - credits_used,
        "amount_display": f"¥{(total_price - credits_used) / 100:.2f}",
        "status": "confirmed",
    }


@router.get("/orders")
async def list_orders(user: dict = Depends(require_parent)):
    """获取我的文创订单"""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT mo.id, mo.status, mo.total_price, mo.created_at,
                      mt.name_zh, mt.name_en
               FROM merch_orders mo
               JOIN merch_types mt ON mt.id = mo.merch_type_id
               WHERE mo.parent_id = ?
               ORDER BY mo.created_at DESC""",
            (user["user_id"],),
        ).fetchall()
    return {
        "orders": [
            {**dict(r), "price_display": f"¥{r['total_price'] / 100:.2f}"}
            for r in rows
        ],
        "total": len(rows),
    }
