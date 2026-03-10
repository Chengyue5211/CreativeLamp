"""
绘创前程 — 认证服务
家长注册 → 绑定孩子 → 登录
"""
import re
import uuid
from typing import Optional

from core.database import get_db
from core.security import hash_password, verify_password, create_access_token


def register_parent(phone: str, password: str, nickname: str = "") -> dict:
    """家长注册"""
    if not re.match(r"^1[3-9]\d{9}$", phone):
        raise ValueError("手机号格式不正确")
    if len(password) < 6:
        raise ValueError("密码至少6位")

    with get_db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE phone = ?", (phone,)).fetchone()
        if existing:
            raise ValueError("该手机号已注册")

        cursor = conn.execute(
            """INSERT INTO users (phone, password_hash, role, nickname)
               VALUES (?, ?, 'parent', ?)""",
            (phone, hash_password(password), nickname or f"家长{phone[-4:]}")
        )
        parent_id = cursor.lastrowid

    token = create_access_token(parent_id, "parent")
    return {
        "user_id": parent_id,
        "role": "parent",
        "nickname": nickname or f"家长{phone[-4:]}",
        "token": token,
    }


def add_child(parent_id: int, nickname: str, age: int, gender: str = "unknown") -> dict:
    """家长添加孩子"""
    if age < 2 or age > 18:
        raise ValueError("年龄应在2-18岁之间")

    level_grade = _age_to_level(age)

    with get_db() as conn:
        # 创建孩子用户
        cursor = conn.execute(
            """INSERT INTO users (role, nickname, age, gender, level_grade)
               VALUES ('child', ?, ?, ?, ?)""",
            (nickname, age, gender, level_grade)
        )
        child_id = cursor.lastrowid

        # 建立亲子关系
        conn.execute(
            """INSERT INTO user_relations (parent_id, child_id, relation_type)
               VALUES (?, ?, 'parent_child')""",
            (parent_id, child_id)
        )

    return {
        "child_id": child_id,
        "nickname": nickname,
        "age": age,
        "level_grade": level_grade,
    }


def login(phone: str, password: str) -> dict:
    """登录"""
    with get_db() as conn:
        user = conn.execute(
            "SELECT id, password_hash, role, nickname FROM users WHERE phone = ? AND is_active = 1",
            (phone,)
        ).fetchone()

    if not user:
        raise ValueError("手机号未注册")
    if not verify_password(password, user["password_hash"]):
        raise ValueError("密码错误")

    token = create_access_token(user["id"], user["role"])
    return {
        "user_id": user["id"],
        "role": user["role"],
        "nickname": user["nickname"],
        "token": token,
    }


def get_children(parent_id: int) -> list:
    """获取家长绑定的所有孩子"""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT u.id, u.nickname, u.age, u.gender, u.level_grade, u.avatar_url
               FROM users u
               JOIN user_relations r ON r.child_id = u.id
               WHERE r.parent_id = ? AND r.relation_type = 'parent_child' AND u.is_active = 1""",
            (parent_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def switch_to_child(parent_id: int, child_id: int) -> dict:
    """家长切换到孩子模式，生成孩子的访问令牌"""
    with get_db() as conn:
        relation = conn.execute(
            """SELECT id FROM user_relations
               WHERE parent_id = ? AND child_id = ? AND relation_type = 'parent_child' AND is_active = 1""",
            (parent_id, child_id)
        ).fetchone()

    if not relation:
        raise ValueError("无权访问该孩子账户")

    with get_db() as conn:
        child = conn.execute(
            "SELECT id, nickname, age, level_grade FROM users WHERE id = ?",
            (child_id,)
        ).fetchone()

    token = create_access_token(child["id"], "child", {"parent_id": parent_id})
    return {
        "child_id": child["id"],
        "nickname": child["nickname"],
        "age": child["age"],
        "level_grade": child["level_grade"],
        "token": token,
    }


def _age_to_level(age: int) -> str:
    """根据年龄自动分配九级体系等级"""
    if age <= 4:
        return "prep"
    elif age <= 5:
        return "beginner_upper"
    elif age <= 6:
        return "beginner_lower"
    elif age <= 8:
        return "mid_upper"
    elif age <= 10:
        return "mid_lower"
    elif age <= 12:
        return "adv_upper"
    elif age <= 14:
        return "adv_lower"
    else:
        return "super_upper"
