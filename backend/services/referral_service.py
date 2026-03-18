"""
绘创前程 — 推广裂变服务
两级分销 + 学币奖励体系

奖励结构:
  - 推荐人(L1): 被邀请人注册 → +50学币
  - 推荐人(L2): 被邀请人的邀请人也获 → +10学币
  - 被邀请人: 注册即得 → +30学币 (欢迎奖励)
  - 里程碑: 5/10/25次成功推荐 → 额外奖励

防刷机制:
  - 同IP 24h内最多3次注册
  - 邀请码不可自用
  - 奖励仅在被邀请人完成注册后发放
"""
import os
import secrets
import string
from datetime import datetime, timezone, timedelta

from core.database import get_db

# 奖励配置
REWARD_L1_SIGNUP = 50       # 直接推荐注册奖励
REWARD_L2_SIGNUP = 10       # 间接推荐注册奖励
REWARD_WELCOME = 30         # 被邀请人欢迎奖励
MILESTONE_REWARDS = {       # 里程碑奖励
    5: 100,
    10: 300,
    25: 800,
    50: 2000,
}

# 防刷配置
MAX_SIGNUPS_PER_IP_24H = 3


def generate_invite_code() -> str:
    """生成6位邀请码 (大写字母+数字，去掉易混淆字符)"""
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # 去掉 I O 0 1
    while True:
        code = "".join(secrets.choice(chars) for _ in range(6))
        with get_db() as conn:
            exists = conn.execute(
                "SELECT 1 FROM users WHERE invite_code = ?", (code,)
            ).fetchone()
        if not exists:
            return code


def ensure_invite_code(user_id: int) -> str:
    """确保用户有邀请码，没有就生成一个"""
    with get_db() as conn:
        row = conn.execute(
            "SELECT invite_code FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if row and row["invite_code"]:
            return row["invite_code"]

    code = generate_invite_code()
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET invite_code = ? WHERE id = ? AND invite_code IS NULL",
            (code, user_id),
        )
        # 可能并发，重新读取
        row = conn.execute(
            "SELECT invite_code FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    return row["invite_code"]


def validate_invite_code(code: str) -> dict | None:
    """验证邀请码，返回邀请人信息"""
    if not code or len(code) != 6:
        return None
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, nickname, avatar_url FROM users WHERE invite_code = ? AND is_active = 1",
            (code.upper(),)
        ).fetchone()
    if row:
        return {"user_id": row["id"], "nickname": row["nickname"], "avatar_url": row["avatar_url"] or ""}
    return None


def apply_referral(invitee_id: int, invite_code: str) -> dict:
    """
    注册时应用邀请关系：
    1. 绑定邀请关系
    2. 发放三方奖励 (邀请人L1 + 间接邀请人L2 + 被邀请人)
    3. 检查里程碑
    返回奖励摘要
    """
    inviter = validate_invite_code(invite_code)
    if not inviter:
        return {"applied": False, "reason": "无效邀请码"}

    inviter_id = inviter["user_id"]
    if inviter_id == invitee_id:
        return {"applied": False, "reason": "不能使用自己的邀请码"}

    with get_db() as conn:
        # 检查是否已有邀请关系
        existing = conn.execute(
            "SELECT id FROM referrals WHERE invitee_id = ?", (invitee_id,)
        ).fetchone()
        if existing:
            return {"applied": False, "reason": "已绑定邀请人"}

        # 创建邀请关系
        cursor = conn.execute(
            """INSERT INTO referrals (inviter_id, invitee_id, invite_code, status)
               VALUES (?, ?, ?, 'registered')""",
            (inviter_id, invitee_id, invite_code.upper()),
        )
        referral_id = cursor.lastrowid

        # 更新被邀请人的 referred_by_id
        conn.execute(
            "UPDATE users SET referred_by_id = ? WHERE id = ?",
            (inviter_id, invitee_id),
        )

        rewards = []

        # L1 奖励：推荐人
        _add_credit(conn, inviter_id, REWARD_L1_SIGNUP, "referral_signup",
                     referral_id, "推荐新用户注册奖励")
        rewards.append({"recipient": "inviter", "amount": REWARD_L1_SIGNUP})

        # 创建奖励记录
        conn.execute(
            """INSERT INTO referral_rewards (referral_id, reward_type, recipient_id, reward_amount, status)
               VALUES (?, 'register_bonus', ?, ?, 'settled')""",
            (referral_id, inviter_id, REWARD_L1_SIGNUP),
        )

        # L2 奖励：邀请人的邀请人
        l2_inviter = conn.execute(
            "SELECT referred_by_id FROM users WHERE id = ?", (inviter_id,)
        ).fetchone()
        if l2_inviter and l2_inviter["referred_by_id"]:
            l2_id = l2_inviter["referred_by_id"]
            _add_credit(conn, l2_id, REWARD_L2_SIGNUP, "referral_l2_signup",
                         referral_id, "二级推荐注册奖励")
            rewards.append({"recipient": "l2_inviter", "amount": REWARD_L2_SIGNUP})

            conn.execute(
                """INSERT INTO referral_rewards (referral_id, reward_type, recipient_id, reward_amount, status)
                   VALUES (?, 'register_bonus', ?, ?, 'settled')""",
                (referral_id, l2_id, REWARD_L2_SIGNUP),
            )

        # 被邀请人欢迎奖励
        _add_credit(conn, invitee_id, REWARD_WELCOME, "welcome_bonus",
                     referral_id, "受邀注册欢迎奖励")
        rewards.append({"recipient": "invitee", "amount": REWARD_WELCOME})

        # 检查里程碑
        milestone_reward = _check_milestones(conn, inviter_id)
        if milestone_reward:
            rewards.append({"recipient": "inviter_milestone", "amount": milestone_reward})

    return {"applied": True, "rewards": rewards}


def _add_credit(conn, user_id: int, amount: int, tx_type: str,
                reference_id: int = None, description: str = ""):
    """内部：添加学币并记录流水"""
    # 更新余额
    conn.execute(
        "UPDATE users SET credit_balance = COALESCE(credit_balance, 0) + ? WHERE id = ?",
        (amount, user_id),
    )
    # 查询更新后余额
    row = conn.execute(
        "SELECT COALESCE(credit_balance, 0) as bal FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    balance_after = row["bal"] if row else amount

    conn.execute(
        """INSERT INTO credit_transactions (user_id, amount, balance_after, tx_type, reference_id, description)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, amount, balance_after, tx_type, reference_id, description),
    )


def _check_milestones(conn, inviter_id: int) -> int | None:
    """检查并发放里程碑奖励，返回奖励金额或None"""
    count = conn.execute(
        "SELECT COUNT(*) as cnt FROM referrals WHERE inviter_id = ? AND status != 'invalid'",
        (inviter_id,)
    ).fetchone()["cnt"]

    if count not in MILESTONE_REWARDS:
        return None

    reward = MILESTONE_REWARDS[count]
    # 检查是否已发放过该里程碑
    already = conn.execute(
        """SELECT 1 FROM credit_transactions
           WHERE user_id = ? AND tx_type = 'milestone_bonus' AND description LIKE ?""",
        (inviter_id, f"%{count}次推荐%"),
    ).fetchone()
    if already:
        return None

    _add_credit(conn, inviter_id, reward, "milestone_bonus",
                None, f"达成{count}次推荐里程碑奖励")
    return reward


def get_referral_dashboard(user_id: int) -> dict:
    """获取用户推广仪表盘数据"""
    code = ensure_invite_code(user_id)

    with get_db() as conn:
        # 基本信息
        user = conn.execute(
            "SELECT COALESCE(credit_balance, 0) as credit_balance FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        # 推荐统计
        total = conn.execute(
            "SELECT COUNT(*) as cnt FROM referrals WHERE inviter_id = ? AND status != 'invalid'",
            (user_id,)
        ).fetchone()["cnt"]

        # 本月推荐
        month_start = datetime.now().strftime("%Y-%m-01")
        monthly = conn.execute(
            "SELECT COUNT(*) as cnt FROM referrals WHERE inviter_id = ? AND status != 'invalid' AND created_at >= ?",
            (user_id, month_start),
        ).fetchone()["cnt"]

        # 总收入
        total_earned = conn.execute(
            """SELECT COALESCE(SUM(amount), 0) as total FROM credit_transactions
               WHERE user_id = ? AND amount > 0""",
            (user_id,)
        ).fetchone()["total"]

        # 下一个里程碑
        next_milestone = None
        for threshold in sorted(MILESTONE_REWARDS.keys()):
            if total < threshold:
                next_milestone = {"target": threshold, "current": total, "reward": MILESTONE_REWARDS[threshold]}
                break

    return {
        "invite_code": code,
        "credit_balance": user["credit_balance"] if user else 0,
        "total_referrals": total,
        "monthly_referrals": monthly,
        "total_earned": total_earned,
        "next_milestone": next_milestone,
    }


def get_referral_list(user_id: int, page: int = 1, limit: int = 20) -> dict:
    """获取推荐记录列表"""
    offset = (page - 1) * limit
    with get_db() as conn:
        total = conn.execute(
            "SELECT COUNT(*) as cnt FROM referrals WHERE inviter_id = ?", (user_id,)
        ).fetchone()["cnt"]

        rows = conn.execute(
            """SELECT r.id, r.status, r.created_at,
                      u.nickname, u.avatar_url
               FROM referrals r
               JOIN users u ON u.id = r.invitee_id
               WHERE r.inviter_id = ?
               ORDER BY r.created_at DESC
               LIMIT ? OFFSET ?""",
            (user_id, limit, offset),
        ).fetchall()

    return {
        "total": total,
        "page": page,
        "items": [
            {
                "id": r["id"],
                "nickname": r["nickname"],
                "avatar_url": r["avatar_url"] or "",
                "status": r["status"],
                "created_at": r["created_at"],
            }
            for r in rows
        ],
    }


def get_reward_history(user_id: int, page: int = 1, limit: int = 20) -> dict:
    """获取学币流水记录"""
    offset = (page - 1) * limit
    with get_db() as conn:
        total = conn.execute(
            "SELECT COUNT(*) as cnt FROM credit_transactions WHERE user_id = ?",
            (user_id,)
        ).fetchone()["cnt"]

        rows = conn.execute(
            """SELECT id, amount, balance_after, tx_type, description, created_at
               FROM credit_transactions
               WHERE user_id = ?
               ORDER BY created_at DESC
               LIMIT ? OFFSET ?""",
            (user_id, limit, offset),
        ).fetchall()

    return {
        "total": total,
        "page": page,
        "items": [dict(r) for r in rows],
    }


def get_credit_balance(user_id: int) -> int:
    """获取用户学币余额"""
    with get_db() as conn:
        row = conn.execute(
            "SELECT COALESCE(credit_balance, 0) as bal FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
    return row["bal"] if row else 0
