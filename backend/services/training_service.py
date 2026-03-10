"""
绘创前程 — 训练引擎服务
核心逻辑：根据孩子年龄和等级，生成个性化训练任务

双训练体系：
- 模块A：原型组合创意绘画（108种线条原型的识别→模仿→补全→迁移→创作）
- 模块B：图形变形与结构生成（9种基础图形 × 30种变形方法）
"""
import json
import random
from datetime import datetime
from typing import Optional

from core.database import get_db
from data.prototypes import LINE_PROTOTYPE_CATEGORIES, SHAPE_PROTOTYPES, get_all_line_prototypes
from data.transforms import TRANSFORM_METHODS, COMBINATION_MODES, INCREASE_SUBTYPES


# ============================================================
# 九级难度梯度定义
# ============================================================
LEVEL_CONFIG = {
    "prep": {
        "name": "准备级", "age_range": "3-4岁",
        "module_a": {"max_prototypes": 1, "composition_modes": ["repeat"], "task_types": ["identify", "imitate"]},
        "module_b": {"max_shapes": 1, "max_transforms": 1, "task_types": ["identify"]},
    },
    "beginner_upper": {
        "name": "初级上", "age_range": "4-5岁",
        "module_a": {"max_prototypes": 2, "composition_modes": ["repeat", "arrange"], "task_types": ["identify", "imitate", "complete"]},
        "module_b": {"max_shapes": 1, "max_transforms": 2, "task_types": ["identify", "transform"]},
    },
    "beginner_lower": {
        "name": "初级下", "age_range": "5-6岁",
        "module_a": {"max_prototypes": 3, "composition_modes": ["repeat", "arrange", "density", "thickness"], "task_types": ["identify", "imitate", "complete", "transfer"]},
        "module_b": {"max_shapes": 1, "max_transforms": 3, "task_types": ["identify", "transform", "generate"]},
    },
    "mid_upper": {
        "name": "中级上", "age_range": "6-8岁",
        "module_a": {"max_prototypes": 4, "composition_modes": ["repeat", "arrange", "density", "thickness", "direction", "surround"], "task_types": ["identify", "imitate", "complete", "transfer", "create"]},
        "module_b": {"max_shapes": 2, "max_transforms": 4, "task_types": ["identify", "transform", "generate"]},
    },
    "mid_lower": {
        "name": "中级下", "age_range": "8-10岁",
        "module_a": {"max_prototypes": 5, "composition_modes": ["repeat", "arrange", "density", "thickness", "direction", "surround", "cross", "zone_fill"], "task_types": ["imitate", "complete", "transfer", "create", "contour_decorate"]},
        "module_b": {"max_shapes": 2, "max_transforms": 5, "task_types": ["transform", "generate"]},
    },
    "adv_upper": {
        "name": "高级上", "age_range": "10-12岁",
        "module_a": {"max_prototypes": 6, "composition_modes": ["repeat", "arrange", "density", "thickness", "direction", "surround", "cross", "zone_fill", "center_spread"], "task_types": ["complete", "transfer", "create", "contour_decorate", "expand"]},
        "module_b": {"max_shapes": 3, "max_transforms": 6, "task_types": ["transform", "generate"]},
    },
    "adv_lower": {
        "name": "高级下", "age_range": "12岁以上",
        "module_a": {"max_prototypes": 6, "composition_modes": ["repeat", "arrange", "density", "thickness", "direction", "surround", "cross", "zone_fill", "center_spread"], "task_types": ["create", "contour_decorate", "expand"]},
        "module_b": {"max_shapes": 3, "max_transforms": 7, "task_types": ["generate"]},
    },
    "super_upper": {
        "name": "超级上", "age_range": "初中",
        "module_a": {"max_prototypes": 7, "composition_modes": ["repeat", "arrange", "density", "thickness", "direction", "surround", "cross", "zone_fill", "center_spread"], "task_types": ["create", "contour_decorate", "expand"]},
        "module_b": {"max_shapes": 4, "max_transforms": 8, "task_types": ["generate"]},
    },
    "super_lower": {
        "name": "超级下", "age_range": "初中以上",
        "module_a": {"max_prototypes": 8, "composition_modes": ["repeat", "arrange", "density", "thickness", "direction", "surround", "cross", "zone_fill", "center_spread"], "task_types": ["create", "contour_decorate", "expand"]},
        "module_b": {"max_shapes": 5, "max_transforms": 10, "task_types": ["generate"]},
    },
}

# 任务类型的中文名和说明
TASK_TYPE_INFO = {
    "identify":           {"name": "识别任务", "instruction": "看一看，认一认这些线条原型", "icon": "👁️", "estimated_minutes": 5},
    "imitate":            {"name": "模仿任务", "instruction": "照着示范，在纸上画一画", "icon": "✏️", "estimated_minutes": 10},
    "complete":           {"name": "补全任务", "instruction": "画面缺了一部分，把它补完整", "icon": "🧩", "estimated_minutes": 10},
    "transfer":           {"name": "迁移任务", "instruction": "用学过的线条，装饰一个新的图形", "icon": "🔄", "estimated_minutes": 15},
    "create":             {"name": "创作任务", "instruction": "用这些线条原型，自由创作你的作品", "icon": "🎨", "estimated_minutes": 20},
    "contour_decorate":   {"name": "轮廓装饰", "instruction": "给这个轮廓填上美丽的线条装饰", "icon": "🖼️", "estimated_minutes": 20},
    "expand":             {"name": "扩图任务", "instruction": "把小图扩展成大画面", "icon": "🔍", "estimated_minutes": 25},
    "transform":          {"name": "变形任务", "instruction": "用变形魔法，把基础图形变成新的东西", "icon": "✨", "estimated_minutes": 15},
    "generate":           {"name": "生成任务", "instruction": "组合变形方法，创造一个全新的角色或物体", "icon": "🌟", "estimated_minutes": 25},
}


def generate_daily_task(child_id: int) -> dict:
    """
    为孩子生成每日训练任务（一个模块A + 一个模块B）
    核心算法：根据等级选择合适的原型数量、变形方法数量和任务类型
    """
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

    # 生成模块A任务
    task_a = _generate_module_a_task(child_id, config["module_a"], age)

    # 生成模块B任务
    task_b = _generate_module_b_task(child_id, config["module_b"], age)

    # 存入数据库
    with get_db() as conn:
        # 检查今天是否已有任务
        today = datetime.now().strftime("%Y-%m-%d")
        existing = conn.execute(
            """SELECT id FROM tasks
               WHERE child_id = ? AND date(assigned_at) = ?""",
            (child_id, today)
        ).fetchone()

        if existing:
            # 今天已有任务，返回已有的
            return get_today_tasks(child_id)

        # 先保存任务模板（如果不存在）
        template_a_id = _ensure_task_template(conn, task_a)
        template_b_id = _ensure_task_template(conn, task_b)

        # 创建任务实例
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
    today = datetime.now().strftime("%Y-%m-%d")
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
    """获取任务详情（含完整的原型/变形数据，用于前端渲染示范）"""
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

    # 查找完整的原型数据
    all_lines = get_all_line_prototypes()
    line_map = {p["id"]: p for p in all_lines}
    shape_map = {s["id"]: s for s in SHAPE_PROTOTYPES}

    prototypes_data = []
    for pid in prototype_ids:
        if pid in line_map:
            prototypes_data.append(line_map[pid])
        elif pid in shape_map:
            prototypes_data.append(shape_map[pid])

    # 查找完整的变形方法数据
    transform_map = {t["id"]: t for t in TRANSFORM_METHODS}
    transforms_data = [transform_map[tid] for tid in transform_ids if tid in transform_map]

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
        "transforms": transforms_data,
        "requirement": json.loads(row["requirement_json"] or "{}"),
    }


def update_task_status(task_id: int, child_id: int, status: str) -> dict:
    """更新任务状态"""
    valid_statuses = ("in_progress", "submitted", "evaluated")
    if status not in valid_statuses:
        raise ValueError(f"无效状态，可选: {valid_statuses}")

    with get_db() as conn:
        task = conn.execute(
            "SELECT id, status FROM tasks WHERE id = ? AND child_id = ?",
            (task_id, child_id)
        ).fetchone()
        if not task:
            raise ValueError("任务不存在")

        update_fields = {"status": status}
        if status == "submitted":
            update_fields["submitted_at"] = datetime.now().isoformat()
        elif status == "evaluated":
            update_fields["evaluated_at"] = datetime.now().isoformat()

        set_clause = ", ".join(f"{k} = ?" for k in update_fields)
        values = list(update_fields.values()) + [task_id]
        conn.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", values)

    return {"task_id": task_id, "status": status}


def get_prototype_library(module: str = None, category: str = None) -> list:
    """获取原型库，支持按模块/类别筛选"""
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


def get_transform_library(category: str = None, max_age: int = None) -> list:
    """获取变形方法库，支持筛选"""
    methods = TRANSFORM_METHODS
    if category:
        methods = [m for m in methods if m["category"] == category]
    if max_age is not None:
        methods = [m for m in methods if m["min_age"] <= max_age]
    return methods


# ============================================================
# 内部辅助方法
# ============================================================

def _generate_module_a_task(child_id: int, config: dict, age: int) -> dict:
    """生成模块A任务：原型组合创意绘画"""
    max_protos = config["max_prototypes"]
    task_type = random.choice(config["task_types"])
    modes = config["composition_modes"]

    # 选择原型数量（根据任务类型调整）
    if task_type in ("identify", "imitate"):
        num_protos = min(2, max_protos)
    elif task_type in ("complete", "transfer"):
        num_protos = min(3, max_protos)
    else:
        num_protos = max_protos

    # 随机选择原型（从不同类别中选，确保多样性）
    all_lines = get_all_line_prototypes()
    categories = list(set(p["category"] for p in all_lines))
    chosen_cats = random.sample(categories, min(num_protos, len(categories)))

    selected_prototypes = []
    for cat in chosen_cats:
        cat_protos = [p for p in all_lines if p["category"] == cat]
        selected_prototypes.append(random.choice(cat_protos))

    # 选择呈现方式
    composition = random.choice(modes)
    comp_info = next((m for m in COMBINATION_MODES if m["id"] == composition), None)

    task_info = TASK_TYPE_INFO[task_type]

    # 生成任务标题
    proto_names = "、".join(p["name_zh"] for p in selected_prototypes)
    title = f"{task_info['name']}：{proto_names}"

    # 生成任务描述
    desc_parts = [task_info["instruction"]]
    if comp_info:
        desc_parts.append(f"呈现方式：{comp_info['name_zh']}——{comp_info['description']}")
    description = "。".join(desc_parts)

    return {
        "module": "A",
        "title": title,
        "description": description,
        "task_type": task_type,
        "difficulty_level": list(LEVEL_CONFIG.keys()).index(
            next(k for k, v in LEVEL_CONFIG.items() if v["module_a"]["max_prototypes"] == max_protos)
        ) + 1,
        "prototype_ids": [p["id"] for p in selected_prototypes],
        "transform_ids": [],
        "requirement": {
            "num_prototypes": num_protos,
            "composition_mode": composition,
            "prototype_details": [
                {"id": p["id"], "name_zh": p["name_zh"], "category": p["category"]}
                for p in selected_prototypes
            ],
        },
        "estimated_minutes": task_info["estimated_minutes"],
        # 前端展示用（不入库）
        "task_type_name": task_info["name"],
        "instruction": task_info["instruction"],
        "icon": task_info["icon"],
        "prototypes": selected_prototypes,
        "transforms": [],
    }


def _generate_module_b_task(child_id: int, config: dict, age: int) -> dict:
    """生成模块B任务：图形变形与结构生成"""
    max_shapes = config["max_shapes"]
    max_transforms = config["max_transforms"]
    task_type = random.choice(config["task_types"])

    # 选择基础图形
    num_shapes = min(random.randint(1, max_shapes), len(SHAPE_PROTOTYPES))
    selected_shapes = random.sample(SHAPE_PROTOTYPES, num_shapes)

    # 选择变形方法（根据年龄过滤）
    available_transforms = [t for t in TRANSFORM_METHODS if t["min_age"] <= age + 1]
    num_transforms = min(random.randint(1, max_transforms), len(available_transforms))
    selected_transforms = random.sample(available_transforms, num_transforms)

    task_info = TASK_TYPE_INFO[task_type]

    # 生成任务标题
    shape_names = "、".join(s["name_zh"] for s in selected_shapes)
    transform_names = "、".join(t["name_zh"] for t in selected_transforms)
    title = f"{task_info['name']}：{shape_names} × {transform_names}"

    # 生成引导问题
    questions = []
    for t in selected_transforms:
        q = t.get("question_template", "")
        for s in selected_shapes:
            questions.append(q.replace("【对象】", s["name_zh"]))

    description = task_info["instruction"]
    if questions:
        description += "。想一想：" + questions[0]

    return {
        "module": "B",
        "title": title,
        "description": description,
        "task_type": task_type,
        "difficulty_level": min(9, num_shapes + num_transforms),
        "prototype_ids": [s["id"] for s in selected_shapes],
        "transform_ids": [t["id"] for t in selected_transforms],
        "requirement": {
            "num_shapes": num_shapes,
            "num_transforms": num_transforms,
            "shapes": [{"id": s["id"], "name_zh": s["name_zh"]} for s in selected_shapes],
            "transforms": [{"id": t["id"], "name_zh": t["name_zh"], "category": t["category"]} for t in selected_transforms],
            "guiding_questions": questions,
            "hints": [h for t in selected_transforms for h in t.get("hints", [])],
        },
        "estimated_minutes": task_info["estimated_minutes"],
        # 前端展示用
        "task_type_name": task_info["name"],
        "instruction": task_info["instruction"],
        "icon": task_info["icon"],
        "prototypes": selected_shapes,
        "transforms": selected_transforms,
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
