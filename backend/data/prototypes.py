"""
绘创前程 — 原型数据库
基于创始人原创理论："没有原型，就没有变形；没有变形，就没有创造"

模块A：108种线条原型（9大类 × 12变式）
模块B：9种基础图形
"""

# ============================================================
# 模块A：9大类开放性线条原型
# 每类12种变式，共108种
# ============================================================

LINE_PROTOTYPE_CATEGORIES = [
    {
        "id": "straight",
        "name_zh": "直线",
        "name_en": "Straight Line",
        "description": "最基础的线条原型，包括横直线、竖直线、斜线、十字线、放射线等12种变式",
        "variants": [
            {"index": 1,  "name_zh": "横直线",   "name_en": "Horizontal Line"},
            {"index": 2,  "name_zh": "竖直线",   "name_en": "Vertical Line"},
            {"index": 3,  "name_zh": "斜线",     "name_en": "Diagonal Line"},
            {"index": 4,  "name_zh": "十字线",   "name_en": "Cross Line"},
            {"index": 5,  "name_zh": "直角线",   "name_en": "Right Angle Line"},
            {"index": 6,  "name_zh": "放射线",   "name_en": "Radial Line"},
            {"index": 7,  "name_zh": "丁字线",   "name_en": "T-Line"},
            {"index": 8,  "name_zh": "土字线",   "name_en": "Earth-Shape Line"},
            {"index": 9,  "name_zh": "田字线",   "name_en": "Grid Line"},
            {"index": 10, "name_zh": "井字线",   "name_en": "Hash Line"},
            {"index": 11, "name_zh": "米字线",   "name_en": "Star-Cross Line"},
            {"index": 12, "name_zh": "网格线",   "name_en": "Mesh Line"},
        ],
    },
    {
        "id": "dashed",
        "name_zh": "虚线",
        "name_en": "Dashed Line",
        "description": "断续的线条原型，通过间隔节奏产生韵律感",
        "variants": [
            {"index": 1,  "name_zh": "短虚线",     "name_en": "Short Dash"},
            {"index": 2,  "name_zh": "长虚线",     "name_en": "Long Dash"},
            {"index": 3,  "name_zh": "点虚线",     "name_en": "Dot Dash"},
            {"index": 4,  "name_zh": "线点虚线",   "name_en": "Dash-Dot"},
            {"index": 5,  "name_zh": "长短虚线",   "name_en": "Long-Short Dash"},
            {"index": 6,  "name_zh": "双点虚线",   "name_en": "Double-Dot Dash"},
            {"index": 7,  "name_zh": "粗虚线",     "name_en": "Thick Dash"},
            {"index": 8,  "name_zh": "细虚线",     "name_en": "Thin Dash"},
            {"index": 9,  "name_zh": "渐变虚线",   "name_en": "Gradient Dash"},
            {"index": 10, "name_zh": "交替虚线",   "name_en": "Alternating Dash"},
            {"index": 11, "name_zh": "装饰虚线",   "name_en": "Decorative Dash"},
            {"index": 12, "name_zh": "节奏虚线",   "name_en": "Rhythmic Dash"},
        ],
    },
    {
        "id": "arc",
        "name_zh": "弧线",
        "name_en": "Arc Line",
        "description": "柔和的弯曲线条，具有自然流动感",
        "variants": [
            {"index": 1,  "name_zh": "弧线",       "name_en": "Arc"},
            {"index": 2,  "name_zh": "叠弧线",     "name_en": "Stacked Arc"},
            {"index": 3,  "name_zh": "彩虹线",     "name_en": "Rainbow Arc"},
            {"index": 4,  "name_zh": "反向弧线",   "name_en": "Reverse Arc"},
            {"index": 5,  "name_zh": "花状弧线",   "name_en": "Flower Arc"},
            {"index": 6,  "name_zh": "山状弧线",   "name_en": "Mountain Arc"},
            {"index": 7,  "name_zh": "三角弧线",   "name_en": "Triangle Arc"},
            {"index": 8,  "name_zh": "元宝形弧线", "name_en": "Ingot Arc"},
            {"index": 9,  "name_zh": "藤线弧线",   "name_en": "Vine Arc"},
            {"index": 10, "name_zh": "波弧线",     "name_en": "Wave Arc"},
            {"index": 11, "name_zh": "对称弧线",   "name_en": "Symmetric Arc"},
            {"index": 12, "name_zh": "连续弧线",   "name_en": "Continuous Arc"},
        ],
    },
    {
        "id": "wave",
        "name_zh": "波浪线",
        "name_en": "Wave Line",
        "description": "连续起伏的线条，如水波、山峦",
        "variants": [
            {"index": 1,  "name_zh": "波浪线",     "name_en": "Wave"},
            {"index": 2,  "name_zh": "上行波浪线", "name_en": "Rising Wave"},
            {"index": 3,  "name_zh": "下行波浪线", "name_en": "Falling Wave"},
            {"index": 4,  "name_zh": "山形波浪线", "name_en": "Mountain Wave"},
            {"index": 5,  "name_zh": "河流波浪线", "name_en": "River Wave"},
            {"index": 6,  "name_zh": "鱼鳞线",     "name_en": "Fish Scale"},
            {"index": 7,  "name_zh": "网状线",     "name_en": "Net Wave"},
            {"index": 8,  "name_zh": "双波浪线",   "name_en": "Double Wave"},
            {"index": 9,  "name_zh": "密波浪线",   "name_en": "Dense Wave"},
            {"index": 10, "name_zh": "疏波浪线",   "name_en": "Sparse Wave"},
            {"index": 11, "name_zh": "粗细波浪线", "name_en": "Varied Wave"},
            {"index": 12, "name_zh": "装饰波浪线", "name_en": "Decorative Wave"},
        ],
    },
    {
        "id": "zigzag",
        "name_zh": "折线/锯齿线",
        "name_en": "Zigzag Line",
        "description": "尖锐转折的线条，充满力量感和节奏感",
        "variants": [
            {"index": 1,  "name_zh": "锯齿线",       "name_en": "Zigzag"},
            {"index": 2,  "name_zh": "上行锯齿线",   "name_en": "Rising Zigzag"},
            {"index": 3,  "name_zh": "下行锯齿线",   "name_en": "Falling Zigzag"},
            {"index": 4,  "name_zh": "M形锯齿线",    "name_en": "M-Zigzag"},
            {"index": 5,  "name_zh": "W形锯齿线",    "name_en": "W-Zigzag"},
            {"index": 6,  "name_zh": "圆形锯齿线",   "name_en": "Circular Zigzag"},
            {"index": 7,  "name_zh": "三角锯齿线",   "name_en": "Triangle Zigzag"},
            {"index": 8,  "name_zh": "阶梯锯齿线",   "name_en": "Step Zigzag"},
            {"index": 9,  "name_zh": "密锯齿线",     "name_en": "Dense Zigzag"},
            {"index": 10, "name_zh": "疏锯齿线",     "name_en": "Sparse Zigzag"},
            {"index": 11, "name_zh": "粗细锯齿线",   "name_en": "Varied Zigzag"},
            {"index": 12, "name_zh": "装饰锯齿线",   "name_en": "Decorative Zigzag"},
        ],
    },
    {
        "id": "spiral",
        "name_zh": "螺旋线",
        "name_en": "Spiral Line",
        "description": "旋转向内或向外的线条，具有生长感和运动感",
        "variants": [
            {"index": 1,  "name_zh": "圆形螺旋线",   "name_en": "Round Spiral"},
            {"index": 2,  "name_zh": "三角螺旋线",   "name_en": "Triangle Spiral"},
            {"index": 3,  "name_zh": "方形螺旋线",   "name_en": "Square Spiral"},
            {"index": 4,  "name_zh": "花朵螺旋线",   "name_en": "Flower Spiral"},
            {"index": 5,  "name_zh": "花枝螺旋线",   "name_en": "Branch Spiral"},
            {"index": 6,  "name_zh": "五角螺旋线",   "name_en": "Pentagon Spiral"},
            {"index": 7,  "name_zh": "双螺旋线",     "name_en": "Double Spiral"},
            {"index": 8,  "name_zh": "蜗牛螺旋线",   "name_en": "Snail Spiral"},
            {"index": 9,  "name_zh": "紧螺旋线",     "name_en": "Tight Spiral"},
            {"index": 10, "name_zh": "松螺旋线",     "name_en": "Loose Spiral"},
            {"index": 11, "name_zh": "渐变螺旋线",   "name_en": "Gradient Spiral"},
            {"index": 12, "name_zh": "装饰螺旋线",   "name_en": "Decorative Spiral"},
        ],
    },
    {
        "id": "spring",
        "name_zh": "弹簧线",
        "name_en": "Spring Line",
        "description": "具有弹性和动态感的连续环绕线条",
        "variants": [
            {"index": 1,  "name_zh": "圆弹簧线",     "name_en": "Round Spring"},
            {"index": 2,  "name_zh": "椭圆弹簧线",   "name_en": "Oval Spring"},
            {"index": 3,  "name_zh": "三角弹簧线",   "name_en": "Triangle Spring"},
            {"index": 4,  "name_zh": "方弹簧线",     "name_en": "Square Spring"},
            {"index": 5,  "name_zh": "紧弹簧线",     "name_en": "Tight Spring"},
            {"index": 6,  "name_zh": "松弹簧线",     "name_en": "Loose Spring"},
            {"index": 7,  "name_zh": "渐变弹簧线",   "name_en": "Gradient Spring"},
            {"index": 8,  "name_zh": "双弹簧线",     "name_en": "Double Spring"},
            {"index": 9,  "name_zh": "花形弹簧线",   "name_en": "Flower Spring"},
            {"index": 10, "name_zh": "波浪弹簧线",   "name_en": "Wave Spring"},
            {"index": 11, "name_zh": "扭转弹簧线",   "name_en": "Twist Spring"},
            {"index": 12, "name_zh": "装饰弹簧线",   "name_en": "Decorative Spring"},
        ],
    },
    {
        "id": "castle",
        "name_zh": "城墙线",
        "name_en": "Castle Line",
        "description": "方形凹凸交替的线条，如城墙垛口",
        "variants": [
            {"index": 1,  "name_zh": "城墙线",       "name_en": "Castle"},
            {"index": 2,  "name_zh": "口形城墙线",   "name_en": "Square Castle"},
            {"index": 3,  "name_zh": "串城墙线",     "name_en": "String Castle"},
            {"index": 4,  "name_zh": "高低楼房线",   "name_en": "Building Castle"},
            {"index": 5,  "name_zh": "芭蕉叶城墙线", "name_en": "Banana Leaf Castle"},
            {"index": 6,  "name_zh": "阶梯城墙线",   "name_en": "Step Castle"},
            {"index": 7,  "name_zh": "圆顶城墙线",   "name_en": "Dome Castle"},
            {"index": 8,  "name_zh": "尖顶城墙线",   "name_en": "Spire Castle"},
            {"index": 9,  "name_zh": "双层城墙线",   "name_en": "Double Castle"},
            {"index": 10, "name_zh": "密城墙线",     "name_en": "Dense Castle"},
            {"index": 11, "name_zh": "疏城墙线",     "name_en": "Sparse Castle"},
            {"index": 12, "name_zh": "装饰城墙线",   "name_en": "Decorative Castle"},
        ],
    },
    {
        "id": "chinese",
        "name_zh": "中式纹样线",
        "name_en": "Chinese Pattern Line",
        "description": "源自中国传统装饰的经典纹样线条",
        "variants": [
            {"index": 1,  "name_zh": "回纹线",       "name_en": "Fret Pattern"},
            {"index": 2,  "name_zh": "云纹线",       "name_en": "Cloud Pattern"},
            {"index": 3,  "name_zh": "如意纹",       "name_en": "Ruyi Pattern"},
            {"index": 4,  "name_zh": "万字纹",       "name_en": "Wan Pattern"},
            {"index": 5,  "name_zh": "卷草纹",       "name_en": "Scroll Pattern"},
            {"index": 6,  "name_zh": "水纹线",       "name_en": "Water Pattern"},
            {"index": 7,  "name_zh": "缠枝纹",       "name_en": "Interlocking Pattern"},
            {"index": 8,  "name_zh": "祥云纹",       "name_en": "Auspicious Cloud"},
            {"index": 9,  "name_zh": "龙纹线",       "name_en": "Dragon Pattern"},
            {"index": 10, "name_zh": "凤纹线",       "name_en": "Phoenix Pattern"},
            {"index": 11, "name_zh": "莲纹线",       "name_en": "Lotus Pattern"},
            {"index": 12, "name_zh": "几何纹线",     "name_en": "Geometric Pattern"},
        ],
    },
]

# ============================================================
# 模块B：9种基础图形原型
# ============================================================

SHAPE_PROTOTYPES = [
    {"id": "shape_circle",    "name_zh": "圆",     "name_en": "Circle"},
    {"id": "shape_square",    "name_zh": "方",     "name_en": "Square"},
    {"id": "shape_triangle",  "name_zh": "三角",   "name_en": "Triangle"},
    {"id": "shape_ellipse",   "name_zh": "椭圆",   "name_en": "Ellipse"},
    {"id": "shape_semicircle","name_zh": "半圆",   "name_en": "Semicircle"},
    {"id": "shape_teardrop",  "name_zh": "水滴形", "name_en": "Teardrop"},
    {"id": "shape_leaf",      "name_zh": "叶形",   "name_en": "Leaf"},
    {"id": "shape_cloud",     "name_zh": "云形",   "name_en": "Cloud"},
    {"id": "shape_capsule",   "name_zh": "胶囊形", "name_en": "Capsule"},
]


def get_all_line_prototypes():
    """获取全部108种线条原型的扁平列表"""
    result = []
    for cat in LINE_PROTOTYPE_CATEGORIES:
        for v in cat["variants"]:
            result.append({
                "id": f"line_{cat['id']}_{v['index']:02d}",
                "module": "A",
                "category": cat["id"],
                "category_name_zh": cat["name_zh"],
                "name_zh": v["name_zh"],
                "name_en": v["name_en"],
                "variant_index": v["index"],
            })
    return result


def get_all_prototypes():
    """获取全部原型（108线条 + 9图形）"""
    lines = get_all_line_prototypes()
    shapes = [
        {
            "id": s["id"],
            "module": "B",
            "category": s["id"].replace("shape_", ""),
            "category_name_zh": "基础图形",
            "name_zh": s["name_zh"],
            "name_en": s["name_en"],
            "variant_index": 1,
        }
        for s in SHAPE_PROTOTYPES
    ]
    return lines + shapes


# 总计: 108 + 9 = 117 个原型
TOTAL_PROTOTYPES = 9 * 12 + 9  # = 117
