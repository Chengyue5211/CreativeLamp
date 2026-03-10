"""
绘创前程 — 模块B：图形变形与结构生成动作
基于创始人原创理论 PRD 定义

核心逻辑：基础形 → 变形动作 → 结构生成 → 个体化增加 → 新对象形成

7种变形与结构生成动作（非思维创造力变形，是绘画图形变形）：
1. 拉长 — 改变比例关系
2. 切分 — 形成内部结构变化
3. 叠加 — 形成层次与新关系
4. 拼接 — 连接形成新整体
5. 缺口与添加 — 挖去或补上部分改变结构
6. 延展 — "往外长"，向外生长扩展
7. 增加 — "往里添"，自由增加新元素（5种子类型）
"""

# ============================================================
# 7种变形与结构生成动作
# ============================================================

TRANSFORM_ACTIONS = [
    {
        "id": "stretch",
        "name_zh": "拉长",
        "name_en": "Stretch",
        "description": "将原有图形向某一方向拉高、拉宽、拉细、拉扁，使其形成新的比例关系",
        "instruction": "试试把这个图形往上拉高，或者往旁边拉宽，看看它变成了什么新形状？",
        "hints": [
            "往上拉会变得又高又瘦",
            "往两边拉会变得又矮又胖",
            "试试只拉图形的一部分",
        ],
        "examples": [
            "圆拉长变成椭圆",
            "正方形拉高变成长方形",
            "三角形拉宽变成扁三角",
        ],
        "sort_order": 1,
    },
    {
        "id": "split",
        "name_zh": "切分",
        "name_en": "Split",
        "description": "把一个整体图形分成两个、三个或更多部分，形成内部结构变化",
        "instruction": "在图形上画几条线，把它切成几块。每一块可以有不同的装饰！",
        "hints": [
            "横着切、竖着切、斜着切效果都不同",
            "切成不等大的块更有趣",
            "切开的部分可以稍微分开一点",
        ],
        "examples": [
            "圆被十字线切成四瓣",
            "方形被对角线切成三角",
            "图形切开后中间留缝隙",
        ],
        "sort_order": 2,
    },
    {
        "id": "overlap",
        "name_zh": "叠加",
        "name_en": "Overlap",
        "description": "让两个或多个图形在空间上重叠，形成层次与新关系",
        "instruction": "把两个图形叠在一起，看看重叠的地方变成了什么新图案？",
        "hints": [
            "大图形和小图形叠在一起",
            "同样的形状错开位置叠加",
            "重叠部分可以画上特别的装饰",
        ],
        "examples": [
            "两个圆叠在一起像眼镜",
            "三角形叠上方形像房子",
            "多个圆层层叠加像花朵",
        ],
        "sort_order": 3,
    },
    {
        "id": "join",
        "name_zh": "拼接",
        "name_en": "Join",
        "description": "把两个或多个不同图形连接起来，形成新的整体对象",
        "instruction": "选几个不同的图形，把它们拼在一起，看能变成什么新东西！",
        "hints": [
            "上下拼接、左右拼接效果不同",
            "不同大小的图形拼在一起更有趣",
            "拼接处可以自然过渡也可以直接连接",
        ],
        "examples": [
            "半圆+长方形=冰棍",
            "圆+三角+长方形=小人",
            "多个方形拼接=城堡",
        ],
        "sort_order": 4,
    },
    {
        "id": "notch_add",
        "name_zh": "缺口与添加",
        "name_en": "Notch & Add",
        "description": "在原有图形中挖掉一部分，或补上一部分，使结构发生明显改变",
        "instruction": "在图形上挖一个洞，或者在边上补一块，看看它变成了什么？",
        "hints": [
            "挖一个缺口像被咬了一口",
            "补上一块像长出了什么",
            "缺口和添加可以同时使用",
        ],
        "examples": [
            "圆挖一个缺口变成吃豆人",
            "方形缺一角变成门",
            "三角形顶上补一个圆变成冰淇淋",
        ],
        "sort_order": 5,
    },
    {
        "id": "extend",
        "name_zh": "延展",
        "name_en": "Extend",
        "description": "从原有结构向外生长、伸展、扩展，使图形形成更大的空间关系或发展方向。延展是'往外长'",
        "instruction": "让图形往外面长出新的东西！像植物发芽一样向外伸展。",
        "hints": [
            "从边缘往外长出线条或形状",
            "像树枝一样向不同方向延伸",
            "延展的部分可以比原来的图形更大",
        ],
        "examples": [
            "圆往外长出触角变成太阳",
            "方形四角延伸变成桌子",
            "图形向下延展变成有脚的角色",
        ],
        "sort_order": 6,
    },
    {
        "id": "increase",
        "name_zh": "增加",
        "name_en": "Increase",
        "description": "在原有图形或结构基础上，自由增加新的线条、细节、部件、复制元素或附属对象，使对象更丰富、更完整或更具个体特征。增加是'往里面添内容'",
        "instruction": "给你的图形添加更多内容！可以画表情、花纹、小部件，让它变成独一无二的角色！",
        "hints": [
            "添加眼睛嘴巴它就有了表情",
            "添加花纹线条它就更好看",
            "添加小部件它就有了新功能",
        ],
        "examples": [
            "圆+眼睛+嘴巴=笑脸",
            "方形+门+窗=房子",
            "三角+花纹+尾巴=小鱼",
        ],
        "sort_order": 7,
    },
]

# ============================================================
# "增加"动作的5种子类型
# ============================================================

INCREASE_SUBTYPES = [
    {
        "id": "detail_add",
        "parent_action": "increase",
        "name_zh": "细节增加",
        "name_en": "Detail Add",
        "description": "在已有形态上添加纹理、表情、花纹等细节，让对象更精致",
        "examples": ["给圆脸画上笑脸表情", "在花瓶上画出花纹", "给动物画上斑点"],
    },
    {
        "id": "line_add",
        "parent_action": "increase",
        "name_zh": "线条增加",
        "name_en": "Line Add",
        "description": "用线条丰富对象的轮廓或内部，如胡须、头发、毛发质感",
        "examples": ["给太阳画出光芒线", "给小猫画上胡须", "给衣服画上条纹"],
    },
    {
        "id": "part_add",
        "parent_action": "increase",
        "name_zh": "部件增加",
        "name_en": "Part Add",
        "description": "给对象添加新的功能性部件，如手、脚、轮子、翅膀",
        "examples": ["给角色添上翅膀", "给机器人加上手臂", "给汽车装上轮子"],
    },
    {
        "id": "duplicate_add",
        "parent_action": "increase",
        "name_zh": "复制增加",
        "name_en": "Duplicate Add",
        "description": "重复某个元素产生节奏感，如多个窗户、一排牙齿",
        "examples": ["大楼上画一排排窗户", "嘴巴里画出一排牙齿", "花园里复制很多花"],
    },
    {
        "id": "accessory_add",
        "parent_action": "increase",
        "name_zh": "附属对象增加",
        "name_en": "Accessory Add",
        "description": "给对象添加独立的附属小物件，如帽子、围巾、手提包",
        "examples": ["给角色戴上帽子", "给房子旁边画一棵树", "给动物加一个蝴蝶结"],
    },
]


# ============================================================
# 模块A：原型组合的呈现方式（构图方式）
# ============================================================

COMBINATION_MODES = [
    {"id": "repeat",          "name_zh": "重复",       "description": "同一原型反复排列，形成节奏感"},
    {"id": "arrange",         "name_zh": "排列",       "description": "多种原型按规律排列，形成有序的画面"},
    {"id": "density",         "name_zh": "疏密变化",   "description": "通过线条疏密产生视觉节奏和层次"},
    {"id": "thickness",       "name_zh": "粗细变化",   "description": "改变线条粗细产生对比和层次"},
    {"id": "direction",       "name_zh": "方向变化",   "description": "改变线条方向产生动态和运动感"},
    {"id": "surround",        "name_zh": "环绕",       "description": "线条围绕中心环绕排列，形成向心结构"},
    {"id": "cross",           "name_zh": "交叉",       "description": "不同线条交叉叠加，形成编织感"},
    {"id": "zone_fill",       "name_zh": "分区填充",   "description": "将画面分区，用不同原型填充各区"},
    {"id": "center_spread",   "name_zh": "中心扩散",   "description": "从中心向外逐层扩散，由内而外展开"},
]


# ============================================================
# 模块B：难度梯度
# ============================================================

MODULE_B_DIFFICULTY = [
    {"level": 1, "name_zh": "单形变形",   "description": "对一个基础形进行单一变形动作"},
    {"level": 2, "name_zh": "双形拼接",   "description": "两个基础形通过拼接形成新对象"},
    {"level": 3, "name_zh": "多形生成",   "description": "多个基础形组合变形生成复杂结构"},
    {"level": 4, "name_zh": "主题生成",   "description": "围绕主题自由运用多种变形生成角色或场景"},
    {"level": 5, "name_zh": "系列生成",   "description": "生成一组有关联的系列作品或角色家族"},
]


# ============================================================
# 模块B：任务类型
# ============================================================

MODULE_B_TASK_TYPES = [
    {"id": "single_transform",   "name_zh": "单形变形任务",     "description": "对一个基础形执行指定变形动作"},
    {"id": "double_join",        "name_zh": "双形拼接任务",     "description": "选两个基础形拼接成新对象"},
    {"id": "multi_generate",     "name_zh": "多形结构生成任务", "description": "用多个基础形和多种动作生成复杂结构"},
    {"id": "theme_generate",     "name_zh": "主题生成任务",     "description": "围绕给定主题自由创造"},
    {"id": "series_generate",    "name_zh": "系列生成任务",     "description": "创造一组有关联的系列作品"},
    {"id": "detail_increase",    "name_zh": "增加细节任务",     "description": "给已有图形增加细节使其更丰富"},
    {"id": "accessory_increase", "name_zh": "增加附属任务",     "description": "给已有图形添加附属对象"},
]


# ============================================================
# 模块B：作品输出类型
# ============================================================

MODULE_B_OUTPUT_TYPES = [
    {"id": "fantasy_creature",   "name_zh": "奇想生物",   "description": "通过变形生成的奇特生物"},
    {"id": "dream_building",     "name_zh": "梦幻建筑",   "description": "通过拼接叠加生成的建筑"},
    {"id": "structure_character", "name_zh": "结构型角色", "description": "由基础形变形组合而成的角色"},
    {"id": "transform_plant",    "name_zh": "变形植物",   "description": "从基础形延展增加而成的植物"},
    {"id": "generative_object",  "name_zh": "生成式物体", "description": "通过多种动作生成的新物体"},
    {"id": "theme_series",       "name_zh": "主题系列",   "description": "围绕主题的系列作品"},
    {"id": "ip_prototype",       "name_zh": "IP雏形",     "description": "具备文创潜力的小型角色"},
]


# ============================================================
# 便捷函数
# ============================================================

def get_all_transforms():
    """获取7种变形动作"""
    return TRANSFORM_ACTIONS


def get_increase_subtypes():
    """获取增加动作的5种子类型"""
    return INCREASE_SUBTYPES


def get_transform_by_id(action_id: str):
    """根据ID获取变形动作"""
    for a in TRANSFORM_ACTIONS:
        if a["id"] == action_id:
            return a
    return None


TOTAL_TRANSFORM_ACTIONS = len(TRANSFORM_ACTIONS)  # = 7
TOTAL_INCREASE_SUBTYPES = len(INCREASE_SUBTYPES)   # = 5
