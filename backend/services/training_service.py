"""
绘创前程 — 训练引擎服务
核心逻辑：根据孩子年龄和等级，生成个性化训练任务

双训练体系：
- 模块A：原型组合创意绘画（108种线条原型的识别→模仿→补全→迁移→创作）
  - 轮廓装饰任务：从轮廓图形库选一个图形（动物/植物/物品），用线条原型装饰
- 模块B：图形变形与结构生成（9种基础图形 × 7种变形动作）
  7种动作：拉长/切分/叠加/拼接/缺口与添加/延展/增加
"""
import json
import random
from datetime import datetime, timezone
from typing import Optional

from core.database import get_db
from data.prototypes import LINE_PROTOTYPE_CATEGORIES, SHAPE_PROTOTYPES, get_all_line_prototypes
from data.transforms import (
    TRANSFORM_ACTIONS, COMBINATION_MODES, INCREASE_SUBTYPES,
    MODULE_B_DIFFICULTY, MODULE_B_TASK_TYPES, MODULE_B_OUTPUT_TYPES,
)

# ============================================================
# 轮廓图形库（与前端contour-svg.js同步）
# 用于任务生成时推荐轮廓
# ============================================================
CONTOUR_LIBRARY = [
    # ===== 动物 (animals) =====
    {"id": "cat", "name": "猫", "category": "animals", "difficulty": 2, "description": "毛茸茸的小猫咪", "image": "cat.png"},
    {"id": "butterfly", "name": "蝴蝶", "category": "animals", "difficulty": 2, "description": "展翅的蝴蝶", "image": "butterfly.png"},
    {"id": "elephant", "name": "大象", "category": "animals", "difficulty": 3, "description": "正面的大象", "image": "elephant.png"},
    {"id": "panda", "name": "熊猫", "category": "animals", "difficulty": 2, "description": "憨态可掬的国宝", "image": "panda.png"},
    {"id": "owl", "name": "猫头鹰", "category": "animals", "difficulty": 3, "description": "圆滚滚的猫头鹰", "image": "owl.png"},
    {"id": "whale", "name": "鲸鱼", "category": "animals", "difficulty": 2, "description": "海洋中的巨兽", "image": "whale.png"},
    {"id": "crab", "name": "螃蟹", "category": "animals", "difficulty": 3, "description": "张牙舞爪的螃蟹", "image": "crab.png"},
    {"id": "chameleon", "name": "变色龙", "category": "animals", "difficulty": 3, "description": "会变色的小家伙", "image": "chameleon.png"},
    {"id": "ladybug", "name": "瓢虫", "category": "animals", "difficulty": 1, "description": "七星瓢虫", "image": "ladybug.png"},
    {"id": "spider", "name": "蜘蛛", "category": "animals", "difficulty": 2, "description": "八条腿的蜘蛛", "image": "spider.png"},
    {"id": "ant", "name": "蚂蚁", "category": "animals", "difficulty": 2, "description": "勤劳的小蚂蚁", "image": "ant.png"},
    {"id": "squid", "name": "乌贼", "category": "animals", "difficulty": 3, "description": "海洋中的乌贼", "image": "squid.png"},
    {"id": "jellyfish", "name": "水母", "category": "animals", "difficulty": 2, "description": "飘逸的水母", "image": "jellyfish.png"},
    {"id": "beetle", "name": "独角仙", "category": "animals", "difficulty": 3, "description": "威武的独角仙", "image": "beetle.png"},
    {"id": "conch", "name": "海螺", "category": "animals", "difficulty": 2, "description": "美丽的海螺", "image": "conch.png"},
    # ===== 植物与果实 (plants) =====
    {"id": "flower", "name": "花朵", "category": "plants", "difficulty": 1, "description": "六瓣花朵", "image": "flower.png"},
    {"id": "tree", "name": "大树", "category": "plants", "difficulty": 2, "description": "枝繁叶茂的大树", "image": "tree.png"},
    {"id": "leaf", "name": "树叶", "category": "plants", "difficulty": 1, "description": "一片树叶", "image": "leaf.png"},
    {"id": "mushroom", "name": "蘑菇", "category": "plants", "difficulty": 2, "description": "各种蘑菇群", "image": "mushroom.png"},
    {"id": "acorn", "name": "橡果", "category": "plants", "difficulty": 1, "description": "小松鼠爱吃的橡果", "image": "acorn.png"},
    {"id": "pomegranate", "name": "石榴", "category": "plants", "difficulty": 2, "description": "裂开的石榴", "image": "pomegranate.png"},
    # ===== 生活用品 (objects) =====
    {"id": "vase", "name": "花瓶", "category": "objects", "difficulty": 2, "description": "优雅的花瓶", "image": "vase.png"},
    {"id": "cup", "name": "水杯", "category": "objects", "difficulty": 1, "description": "日常水杯", "image": "cup.png"},
    {"id": "umbrella", "name": "雨伞", "category": "objects", "difficulty": 2, "description": "遮风挡雨的伞", "image": "umbrella.png"},
    {"id": "bag", "name": "包", "category": "objects", "difficulty": 2, "description": "漂亮的包", "image": "bag.png"},
    {"id": "hat", "name": "帽子", "category": "objects", "difficulty": 1, "description": "有趣的帽子", "image": "hat.png"},
    {"id": "bottle", "name": "瓶子", "category": "objects", "difficulty": 1, "description": "各种形状的瓶子", "image": "bottle.png"},
    {"id": "plate", "name": "盘子", "category": "objects", "difficulty": 1, "description": "圆形的盘子", "image": "plate.png"},
    {"id": "kettle", "name": "水壶", "category": "objects", "difficulty": 2, "description": "小巧的水壶", "image": "kettle.png"},
    {"id": "clay_pot", "name": "砂锅", "category": "objects", "difficulty": 2, "description": "传统砂锅", "image": "clay_pot.png"},
    {"id": "balloon", "name": "气球", "category": "objects", "difficulty": 1, "description": "飘在空中的气球", "image": "balloon.png"},
    {"id": "shoe", "name": "鞋", "category": "objects", "difficulty": 2, "description": "一双鞋", "image": "shoe.png"},
    # ===== 服饰 (clothing) =====
    {"id": "qipao1", "name": "旗袍·经典", "category": "clothing", "difficulty": 3, "description": "中国传统旗袍", "image": "qipao1.png"},
    {"id": "qipao2", "name": "旗袍·修身", "category": "clothing", "difficulty": 3, "description": "修身版旗袍", "image": "qipao2.png"},
    {"id": "qipao3", "name": "旗袍·宽袖", "category": "clothing", "difficulty": 3, "description": "宽袖旗袍", "image": "qipao3.png"},
    {"id": "qipao4", "name": "旗袍·长款", "category": "clothing", "difficulty": 3, "description": "长款旗袍", "image": "qipao4.png"},
    {"id": "qipao5", "name": "旗袍·无袖", "category": "clothing", "difficulty": 2, "description": "无袖旗袍", "image": "qipao5.png"},
    {"id": "skirt", "name": "裙子", "category": "clothing", "difficulty": 2, "description": "漂亮的裙子", "image": "skirt.png"},
    # ===== 交通工具 (vehicles) =====
    {"id": "car", "name": "汽车", "category": "vehicles", "difficulty": 2, "description": "小汽车", "image": "car.png"},
    {"id": "ship", "name": "轮船", "category": "vehicles", "difficulty": 2, "description": "航行的轮船", "image": "ship.png"},
    {"id": "rocket", "name": "火箭", "category": "vehicles", "difficulty": 2, "description": "飞向太空的火箭", "image": "rocket.png"},
    {"id": "submarine", "name": "潜水艇", "category": "vehicles", "difficulty": 3, "description": "深海潜水艇", "image": "submarine.png"},
    {"id": "hot_air_balloon", "name": "热气球", "category": "vehicles", "difficulty": 2, "description": "五彩热气球", "image": "hot_air_balloon.png"},
    # ===== 奇幻 (fantasy) =====
    {"id": "monster", "name": "怪兽", "category": "fantasy", "difficulty": 3, "description": "可爱的小怪兽", "image": "monster.png"},
]


# ============================================================
# 九级难度梯度定义
# ============================================================
LEVEL_CONFIG = {
    "prep": {
        "name": "准备级", "age_range": "3-4岁",
        "module_a": {"max_prototypes": 1, "composition_modes": ["repeat"], "task_types": ["identify", "imitate"]},
        "module_b": {"max_shapes": 1, "max_actions": 1, "difficulty": 1, "task_types": ["single_transform"]},
    },
    "beginner_upper": {
        "name": "初级上", "age_range": "4-5岁",
        "module_a": {"max_prototypes": 2, "composition_modes": ["repeat", "arrange"], "task_types": ["identify", "imitate", "complete"]},
        "module_b": {"max_shapes": 1, "max_actions": 2, "difficulty": 1, "task_types": ["single_transform"]},
    },
    "beginner_lower": {
        "name": "初级下", "age_range": "5-6岁",
        "module_a": {"max_prototypes": 3, "composition_modes": ["repeat", "arrange", "density", "thickness"], "task_types": ["identify", "imitate", "complete", "transfer"]},
        "module_b": {"max_shapes": 1, "max_actions": 3, "difficulty": 2, "task_types": ["single_transform", "double_join"]},
    },
    "mid_upper": {
        "name": "中级上", "age_range": "6-8岁",
        "module_a": {"max_prototypes": 4, "composition_modes": ["repeat", "arrange", "density", "thickness", "direction", "surround"], "task_types": ["identify", "imitate", "complete", "transfer", "create"]},
        "module_b": {"max_shapes": 2, "max_actions": 4, "difficulty": 2, "task_types": ["single_transform", "double_join", "detail_increase"]},
    },
    "mid_lower": {
        "name": "中级下", "age_range": "8-10岁",
        "module_a": {"max_prototypes": 5, "composition_modes": ["repeat", "arrange", "density", "thickness", "direction", "surround", "cross", "zone_fill"], "task_types": ["imitate", "complete", "transfer", "create", "contour_decorate"]},
        "module_b": {"max_shapes": 2, "max_actions": 5, "difficulty": 3, "task_types": ["single_transform", "double_join", "multi_generate", "detail_increase"]},
    },
    "adv_upper": {
        "name": "高级上", "age_range": "10-12岁",
        "module_a": {"max_prototypes": 6, "composition_modes": ["repeat", "arrange", "density", "thickness", "direction", "surround", "cross", "zone_fill", "center_spread"], "task_types": ["complete", "transfer", "create", "contour_decorate", "expand"]},
        "module_b": {"max_shapes": 3, "max_actions": 6, "difficulty": 4, "task_types": ["double_join", "multi_generate", "theme_generate", "detail_increase", "accessory_increase"]},
    },
    "adv_lower": {
        "name": "高级下", "age_range": "12岁以上",
        "module_a": {"max_prototypes": 6, "composition_modes": ["repeat", "arrange", "density", "thickness", "direction", "surround", "cross", "zone_fill", "center_spread"], "task_types": ["create", "contour_decorate", "expand"]},
        "module_b": {"max_shapes": 3, "max_actions": 7, "difficulty": 4, "task_types": ["multi_generate", "theme_generate", "series_generate"]},
    },
    "super_upper": {
        "name": "超级上", "age_range": "初中",
        "module_a": {"max_prototypes": 7, "composition_modes": ["repeat", "arrange", "density", "thickness", "direction", "surround", "cross", "zone_fill", "center_spread"], "task_types": ["create", "contour_decorate", "expand"]},
        "module_b": {"max_shapes": 4, "max_actions": 7, "difficulty": 5, "task_types": ["theme_generate", "series_generate"]},
    },
    "super_lower": {
        "name": "超级下", "age_range": "初中以上",
        "module_a": {"max_prototypes": 8, "composition_modes": ["repeat", "arrange", "density", "thickness", "direction", "surround", "cross", "zone_fill", "center_spread"], "task_types": ["create", "contour_decorate", "expand"]},
        "module_b": {"max_shapes": 5, "max_actions": 7, "difficulty": 5, "task_types": ["theme_generate", "series_generate"]},
    },
}

# 模块A任务类型
TASK_TYPE_INFO_A = {
    "identify":           {"name": "识别任务", "instruction": "看一看，认一认这些线条原型", "icon": "👁️", "estimated_minutes": 5},
    "imitate":            {"name": "模仿任务", "instruction": "照着示范，在纸上画一画", "icon": "✏️", "estimated_minutes": 10},
    "complete":           {"name": "补全任务", "instruction": "画面缺了一部分，把它补完整", "icon": "🧩", "estimated_minutes": 10},
    "transfer":           {"name": "迁移任务", "instruction": "用学过的线条，装饰一个新的图形", "icon": "🔄", "estimated_minutes": 15},
    "create":             {"name": "创作任务", "instruction": "用这些线条原型，自由创作你的作品", "icon": "🎨", "estimated_minutes": 20},
    "contour_decorate":   {"name": "轮廓装饰", "instruction": "给这个轮廓填上美丽的线条装饰", "icon": "🖼️", "estimated_minutes": 20},
    "expand":             {"name": "扩图任务", "instruction": "把小图扩展成大画面", "icon": "🔍", "estimated_minutes": 25},
}

# 模块B任务类型
TASK_TYPE_INFO_B = {
    "single_transform":   {"name": "单形变形", "instruction": "选一个基础图形，用一种变形动作把它变成新东西", "icon": "🔶", "estimated_minutes": 10},
    "double_join":        {"name": "双形拼接", "instruction": "选两个基础图形，拼接成一个新的角色或物体", "icon": "🔗", "estimated_minutes": 15},
    "multi_generate":     {"name": "多形生成", "instruction": "用多个图形和多种动作，创造一个全新的东西", "icon": "🌟", "estimated_minutes": 20},
    "theme_generate":     {"name": "主题生成", "instruction": "围绕主题，自由运用图形和变形创造作品", "icon": "🎯", "estimated_minutes": 25},
    "series_generate":    {"name": "系列生成", "instruction": "创造一组有关联的系列角色或物品", "icon": "📚", "estimated_minutes": 30},
    "detail_increase":    {"name": "增加细节", "instruction": "给已有的图形添加细节，让它更生动更有趣", "icon": "✨", "estimated_minutes": 15},
    "accessory_increase": {"name": "增加附属", "instruction": "给你的角色添加帽子、翅膀等附属物", "icon": "🎀", "estimated_minutes": 15},
}

# 合并所有任务类型信息（供外部引用）
TASK_TYPE_INFO = {**TASK_TYPE_INFO_A, **TASK_TYPE_INFO_B}


def generate_daily_task(child_id: int) -> dict:
    """为孩子生成每日训练任务（一个模块A + 一个模块B）"""
    with get_db() as conn:
        child = conn.execute(
            "SELECT id, nickname, age, level_grade FROM users WHERE id = ? AND role = 'child'",
            (child_id,)
        ).fetchone()

    if not child:
        raise ValueError("找不到该孩子")

    level = child["level_grade"] or "prep"
    config = LEVEL_CONFIG.get(level, LEVEL_CONFIG["prep"])
    age = child["age"] or 5

    task_a = _generate_module_a_task(child_id, config["module_a"], age)
    task_b = _generate_module_b_task(child_id, config["module_b"], age)

    with get_db() as conn:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        existing = conn.execute(
            "SELECT id FROM tasks WHERE child_id = ? AND date(assigned_at) = ?",
            (child_id, today)
        ).fetchone()

        if existing:
            return get_today_tasks(child_id)

        template_a_id = _ensure_task_template(conn, task_a)
        template_b_id = _ensure_task_template(conn, task_b)

        conn.execute(
            "INSERT INTO tasks (child_id, template_id, status) VALUES (?, ?, 'assigned')",
            (child_id, template_a_id)
        )
        conn.execute(
            "INSERT INTO tasks (child_id, template_id, status) VALUES (?, ?, 'assigned')",
            (child_id, template_b_id)
        )

    return {
        "child_nickname": child["nickname"],
        "level": config["name"],
        "date": today,
        "tasks": [task_a, task_b],
    }


def get_today_tasks(child_id: int) -> dict:
    """获取今天的任务"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with get_db() as conn:
        child = conn.execute(
            "SELECT nickname, level_grade FROM users WHERE id = ?", (child_id,)
        ).fetchone()

        rows = conn.execute(
            """SELECT t.id, t.status, t.assigned_at,
                      tt.module, tt.title, tt.description, tt.task_type,
                      tt.difficulty_level, tt.prototype_ids_json, tt.transform_ids_json,
                      tt.requirement_json, tt.estimated_minutes
               FROM tasks t
               JOIN task_templates tt ON t.template_id = tt.id
               WHERE t.child_id = ? AND date(t.assigned_at) = ?
               ORDER BY tt.module""",
            (child_id, today)
        ).fetchall()

    if not rows:
        return None

    level = child["level_grade"] or "prep"
    config = LEVEL_CONFIG.get(level, LEVEL_CONFIG["prep"])

    tasks = []
    for row in rows:
        task_info = TASK_TYPE_INFO.get(row["task_type"], {})
        tasks.append({
            "task_id": row["id"],
            "module": row["module"],
            "title": row["title"],
            "description": row["description"],
            "task_type": row["task_type"],
            "task_type_name": task_info.get("name", ""),
            "instruction": task_info.get("instruction", ""),
            "icon": task_info.get("icon", ""),
            "estimated_minutes": row["estimated_minutes"] or task_info.get("estimated_minutes", 15),
            "status": row["status"],
            "prototypes": json.loads(row["prototype_ids_json"] or "[]"),
            "transforms": json.loads(row["transform_ids_json"] or "[]"),
            "requirement": json.loads(row["requirement_json"] or "{}"),
        })

    return {
        "child_nickname": child["nickname"],
        "level": config["name"],
        "date": today,
        "tasks": tasks,
    }


def get_task_detail(task_id: int, child_id: int) -> dict:
    """获取任务详情"""
    with get_db() as conn:
        row = conn.execute(
            """SELECT t.id, t.status, t.child_id,
                      tt.module, tt.title, tt.description, tt.task_type,
                      tt.prototype_ids_json, tt.transform_ids_json,
                      tt.requirement_json, tt.estimated_minutes
               FROM tasks t
               JOIN task_templates tt ON t.template_id = tt.id
               WHERE t.id = ? AND t.child_id = ?""",
            (task_id, child_id)
        ).fetchone()

    if not row:
        raise ValueError("任务不存在")

    prototype_ids = json.loads(row["prototype_ids_json"] or "[]")
    transform_ids = json.loads(row["transform_ids_json"] or "[]")

    all_lines = get_all_line_prototypes()
    line_map = {p["id"]: p for p in all_lines}
    shape_map = {s["id"]: s for s in SHAPE_PROTOTYPES}

    prototypes_data = []
    for pid in prototype_ids:
        if pid in line_map:
            prototypes_data.append(line_map[pid])
        elif pid in shape_map:
            prototypes_data.append(shape_map[pid])

    action_map = {a["id"]: a for a in TRANSFORM_ACTIONS}
    actions_data = [action_map[tid] for tid in transform_ids if tid in action_map]

    task_info = TASK_TYPE_INFO.get(row["task_type"], {})

    return {
        "task_id": row["id"],
        "module": row["module"],
        "title": row["title"],
        "description": row["description"],
        "task_type": row["task_type"],
        "task_type_name": task_info.get("name", ""),
        "instruction": task_info.get("instruction", ""),
        "icon": task_info.get("icon", ""),
        "estimated_minutes": row["estimated_minutes"] or task_info.get("estimated_minutes", 15),
        "status": row["status"],
        "prototypes": prototypes_data,
        "transforms": actions_data,
        "requirement": json.loads(row["requirement_json"] or "{}"),
    }


def update_task_status(task_id: int, child_id: int, status: str) -> dict:
    """更新任务状态"""
    ALLOWED_STATUSES = {"in_progress", "submitted", "evaluated"}
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"无效状态，可选: {ALLOWED_STATUSES}")

    with get_db() as conn:
        task = conn.execute(
            "SELECT id, status FROM tasks WHERE id = ? AND child_id = ?",
            (task_id, child_id)
        ).fetchone()
        if not task:
            raise ValueError("任务不存在")

        # 使用固定SQL而非动态字段拼接
        if status == "submitted":
            conn.execute(
                "UPDATE tasks SET status = ?, submitted_at = datetime('now') WHERE id = ?",
                (status, task_id),
            )
        elif status == "evaluated":
            conn.execute(
                "UPDATE tasks SET status = ?, evaluated_at = datetime('now') WHERE id = ?",
                (status, task_id),
            )
        else:
            conn.execute(
                "UPDATE tasks SET status = ? WHERE id = ?",
                (status, task_id),
            )

    return {"task_id": task_id, "status": status}


def get_prototype_library(module: str = None, category: str = None) -> list:
    """获取原型库"""
    if module == "A" or module is None:
        lines = get_all_line_prototypes()
        if category:
            lines = [p for p in lines if p["category"] == category]
    else:
        lines = []

    shapes = []
    if module == "B" or module is None:
        shapes = [
            {
                "id": s["id"],
                "module": "B",
                "category": s["id"].replace("shape_", ""),
                "name_zh": s["name_zh"],
                "name_en": s["name_en"],
            }
            for s in SHAPE_PROTOTYPES
        ]

    return lines + shapes


def get_transform_library() -> list:
    """获取7种变形动作"""
    return TRANSFORM_ACTIONS


# ============================================================
# 内部辅助
# ============================================================

def _generate_module_a_task(child_id: int, config: dict, age: int) -> dict:
    """生成模块A任务"""
    max_protos = config["max_prototypes"]
    task_type = random.choice(config["task_types"])
    modes = config["composition_modes"]

    if task_type in ("identify", "imitate"):
        num_protos = min(2, max_protos)
    elif task_type in ("complete", "transfer"):
        num_protos = min(3, max_protos)
    else:
        num_protos = max_protos

    all_lines = get_all_line_prototypes()
    categories = list(set(p["category"] for p in all_lines))
    chosen_cats = random.sample(categories, min(num_protos, len(categories)))

    selected_prototypes = []
    for cat in chosen_cats:
        cat_protos = [p for p in all_lines if p["category"] == cat]
        selected_prototypes.append(random.choice(cat_protos))

    composition = random.choice(modes)
    comp_info = next((m for m in COMBINATION_MODES if m["id"] == composition), None)

    # 为轮廓装饰/创作/迁移任务推荐一个轮廓图形
    recommended_contour = None
    if task_type in ("contour_decorate", "create", "transfer", "expand"):
        # 根据难度选择合适的轮廓
        max_diff = min(3, 1 + num_protos // 2)
        suitable = [c for c in CONTOUR_LIBRARY if c["difficulty"] <= max_diff]
        if suitable:
            recommended_contour = random.choice(suitable)

    task_info = TASK_TYPE_INFO_A[task_type]
    proto_names = "、".join(p["name_zh"] for p in selected_prototypes)

    if recommended_contour:
        title = f"{task_info['name']}：用{proto_names}装饰{recommended_contour['name']}"
        instruction = f"去图形库找到「{recommended_contour['name']}」，下载打印出来，用{proto_names}把它装饰得漂漂亮亮！"
    else:
        title = f"{task_info['name']}：{proto_names}"
        instruction = task_info["instruction"]

    desc_parts = [instruction]
    if comp_info:
        desc_parts.append(f"呈现方式：{comp_info['name_zh']}——{comp_info['description']}")

    return {
        "module": "A",
        "title": title,
        "description": "。".join(desc_parts),
        "task_type": task_type,
        "difficulty_level": min(9, num_protos),
        "prototype_ids": [p["id"] for p in selected_prototypes],
        "transform_ids": [],
        "requirement": {
            "num_prototypes": num_protos,
            "composition_mode": composition,
            "composition_name": comp_info["name_zh"] if comp_info else "",
            "prototype_details": [
                {"id": p["id"], "name_zh": p["name_zh"], "category": p["category"]}
                for p in selected_prototypes
            ],
            "recommended_contour": recommended_contour,
            "guiding_questions": [
                f"想想看，{proto_names}可以怎样组合？",
                f"试试用{comp_info['name_zh'] if comp_info else '不同方式'}来排列它们",
            ] if comp_info else [],
        },
        "estimated_minutes": task_info["estimated_minutes"],
        "task_type_name": task_info["name"],
        "instruction": instruction,
        "icon": task_info["icon"],
        "prototypes": selected_prototypes,
        "transforms": [],
    }


def _generate_module_b_task(child_id: int, config: dict, age: int) -> dict:
    """生成模块B任务：图形变形与结构生成"""
    max_shapes = config["max_shapes"]
    max_actions = config["max_actions"]
    difficulty = config["difficulty"]
    task_type = random.choice(config["task_types"])

    # 选择基础图形
    num_shapes = min(random.randint(1, max_shapes), len(SHAPE_PROTOTYPES))
    selected_shapes = random.sample(SHAPE_PROTOTYPES, num_shapes)

    # 选择变形动作（从7种中选）
    num_actions = min(random.randint(1, min(max_actions, 3)), len(TRANSFORM_ACTIONS))
    selected_actions = random.sample(TRANSFORM_ACTIONS, num_actions)

    task_info = TASK_TYPE_INFO_B[task_type]

    # 生成标题
    shape_names = "、".join(s["name_zh"] for s in selected_shapes)
    action_names = "、".join(a["name_zh"] for a in selected_actions)
    title = f"{task_info['name']}：{shape_names} → {action_names}"

    # 生成引导
    hints = []
    for a in selected_actions:
        hints.extend(a.get("hints", []))

    examples = []
    for a in selected_actions:
        examples.extend(a.get("examples", []))

    description = task_info["instruction"]

    # 如果是增加类任务，随机选择一种增加子类型
    increase_subtype = None
    if task_type in ("detail_increase", "accessory_increase"):
        if task_type == "detail_increase":
            candidates = [s for s in INCREASE_SUBTYPES if s["id"] in ("detail_add", "line_add")]
        else:
            candidates = [s for s in INCREASE_SUBTYPES if s["id"] in ("part_add", "accessory_add")]
        increase_subtype = random.choice(candidates) if candidates else None

    return {
        "module": "B",
        "title": title,
        "description": description,
        "task_type": task_type,
        "difficulty_level": difficulty,
        "prototype_ids": [s["id"] for s in selected_shapes],
        "transform_ids": [a["id"] for a in selected_actions],
        "requirement": {
            "num_shapes": num_shapes,
            "num_actions": num_actions,
            "shapes": [{"id": s["id"], "name_zh": s["name_zh"]} for s in selected_shapes],
            "actions": [{"id": a["id"], "name_zh": a["name_zh"], "instruction": a["instruction"]} for a in selected_actions],
            "hints": hints[:3],
            "examples": examples[:3],
            "increase_subtype": increase_subtype,
        },
        "estimated_minutes": task_info["estimated_minutes"],
        "task_type_name": task_info["name"],
        "instruction": task_info["instruction"],
        "icon": task_info["icon"],
        "prototypes": selected_shapes,
        "transforms": selected_actions,
    }


def _ensure_task_template(conn, task_data: dict) -> int:
    """确保任务模板存在，返回模板ID"""
    cursor = conn.execute(
        """INSERT INTO task_templates
           (module, title, description, task_type, difficulty_level,
            prototype_ids_json, transform_ids_json, requirement_json, estimated_minutes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            task_data["module"],
            task_data["title"],
            task_data["description"],
            task_data["task_type"],
            task_data.get("difficulty_level", 1),
            json.dumps(task_data.get("prototype_ids", []), ensure_ascii=False),
            json.dumps(task_data.get("transform_ids", []), ensure_ascii=False),
            json.dumps(task_data.get("requirement", {}), ensure_ascii=False),
            task_data.get("estimated_minutes", 15),
        )
    )
    return cursor.lastrowid
