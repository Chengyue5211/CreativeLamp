"""
绘创前程 — 数据库核心模块
统一使用 get_db() 上下文管理器，禁止裸连接
"""
import sqlite3
import os
from contextlib import contextmanager
from pathlib import Path

# 数据库文件路径
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH = DB_DIR / "huichuang.db"


def get_connection() -> sqlite3.Connection:
    """创建数据库连接，启用WAL模式和外键约束"""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    """数据库上下文管理器 — 所有数据库操作必须通过此接口"""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    """初始化数据库表结构"""
    with get_db() as conn:
        conn.executescript(SCHEMA_SQL)
    # 增量迁移：executescript 会自动 COMMIT，需要新连接执行 ALTER TABLE
    with get_db() as conn:
        _migrate_add_columns(conn)


def _migrate_add_columns(conn):
    """增量迁移：安全地为已有表添加新列"""
    migrations = [
        ("users", "invite_code", "TEXT"),
        ("users", "referred_by_id", "INTEGER REFERENCES users(id)"),
        ("users", "credit_balance", "INTEGER DEFAULT 0"),
    ]
    for table, column, col_type in migrations:
        try:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        except Exception:
            pass  # 列已存在，忽略
    # 为新列创建索引
    try:
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_invite_code ON users(invite_code)")
    except Exception:
        pass


# ============================================================
# 数据库表结构 — 14个核心数据对象
# ============================================================
SCHEMA_SQL = """
-- ========================================
-- 1. 用户系统
-- ========================================

-- 统一用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT UNIQUE,
    password_hash TEXT,
    role TEXT NOT NULL CHECK(role IN ('child', 'parent', 'teacher', 'admin')),
    nickname TEXT NOT NULL DEFAULT '',
    avatar_url TEXT DEFAULT '',
    age INTEGER CHECK(age >= 0 AND age <= 100),
    gender TEXT CHECK(gender IN ('male', 'female', 'unknown')) DEFAULT 'unknown',
    level_grade TEXT DEFAULT 'prep',  -- 九级体系: prep/beginner_upper/beginner_lower/mid_upper/mid_lower/adv_upper/adv_lower/super_upper/super_lower
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 用户关系表 (家长-孩子, 老师-孩子)
CREATE TABLE IF NOT EXISTS user_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER NOT NULL REFERENCES users(id),
    child_id INTEGER NOT NULL REFERENCES users(id),
    relation_type TEXT NOT NULL CHECK(relation_type IN ('parent_child', 'teacher_student', 'grandparent_child')),
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(parent_id, child_id, relation_type)
);

-- ========================================
-- 2. 训练系统（双训练核心）
-- ========================================

-- 训练模块注册表
CREATE TABLE IF NOT EXISTS training_modules (
    id TEXT PRIMARY KEY,  -- 'module_a' 或 'module_b'
    name TEXT NOT NULL,
    description TEXT,
    is_active INTEGER DEFAULT 1
);

-- 原型库（模块A的108种线条原型 + 模块B的9种基础图形）
CREATE TABLE IF NOT EXISTS prototypes (
    id TEXT PRIMARY KEY,  -- 如 'line_straight_01', 'shape_circle'
    module TEXT NOT NULL CHECK(module IN ('A', 'B')),
    category TEXT NOT NULL,       -- 大类: straight/dashed/arc/wave/zigzag/spiral/spring/castle/chinese / circle/square/triangle...
    name_zh TEXT NOT NULL,        -- 中文名
    name_en TEXT NOT NULL,        -- 英文名
    variant_index INTEGER DEFAULT 1,  -- 变式编号 (1-12)
    difficulty_level INTEGER DEFAULT 1 CHECK(difficulty_level BETWEEN 1 AND 9),  -- 对应九级
    svg_path TEXT,                -- SVG示意图路径
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

-- 变形动作库（模块B的30种变形方法）
CREATE TABLE IF NOT EXISTS transform_methods (
    id TEXT PRIMARY KEY,  -- 如 'scale_enlarge', 'structure_decompose'
    category TEXT NOT NULL,  -- 7大母类
    name_zh TEXT NOT NULL,
    name_en TEXT NOT NULL,
    icon TEXT DEFAULT '',
    color TEXT DEFAULT '',
    description TEXT,
    question_template TEXT,   -- 引导问题模板，含【对象】占位符
    hints_json TEXT,          -- JSON: 3条启发提示
    examples_json TEXT,       -- JSON: 变形案例
    scoring_keywords_json TEXT,  -- JSON: 评分关键词
    min_age INTEGER DEFAULT 4,
    sort_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

-- 任务模板
CREATE TABLE IF NOT EXISTS task_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module TEXT NOT NULL CHECK(module IN ('A', 'B')),
    title TEXT NOT NULL,
    description TEXT,
    task_type TEXT NOT NULL CHECK(task_type IN (
        'identify', 'imitate', 'complete', 'transfer', 'create',
        'contour_decorate', 'expand',
        'single_transform', 'double_join', 'multi_generate',
        'theme_generate', 'series_generate',
        'detail_increase', 'accessory_increase'
    )),
    difficulty_level INTEGER DEFAULT 1 CHECK(difficulty_level BETWEEN 1 AND 9),
    prototype_ids_json TEXT,     -- JSON: 涉及的原型ID列表
    transform_ids_json TEXT,     -- JSON: 涉及的变形方法ID列表
    requirement_json TEXT,       -- JSON: 任务规则详情
    printable_template_id INTEGER REFERENCES printable_templates(id),
    estimated_minutes INTEGER DEFAULT 15,
    sort_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

-- 任务实例（孩子实际接到的任务）
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL REFERENCES users(id),
    template_id INTEGER NOT NULL REFERENCES task_templates(id),
    status TEXT DEFAULT 'assigned' CHECK(status IN ('assigned', 'in_progress', 'submitted', 'evaluated')),
    assigned_at TEXT DEFAULT (datetime('now')),
    submitted_at TEXT,
    evaluated_at TEXT
);

-- 可打印底稿模板
CREATE TABLE IF NOT EXISTS printable_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_type TEXT NOT NULL CHECK(template_type IN ('contour', 'grid', 'free')),
    title TEXT NOT NULL,
    description TEXT,
    file_path TEXT NOT NULL,  -- PDF/SVG文件路径
    difficulty_level INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

-- ========================================
-- 3. 作品系统
-- ========================================

-- 统一作品表
CREATE TABLE IF NOT EXISTS works (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL REFERENCES users(id),
    task_id INTEGER REFERENCES tasks(id),  -- 可为空（自由上传作品）
    title TEXT NOT NULL DEFAULT '无题',
    description TEXT DEFAULT '',
    image_path TEXT NOT NULL,           -- 原图路径
    thumbnail_path TEXT DEFAULT '',     -- 缩略图路径
    source_type TEXT DEFAULT 'task' CHECK(source_type IN ('task', 'free_upload', 'family_cocreate')),
    visibility TEXT DEFAULT 'private' CHECK(visibility IN ('private', 'family', 'public')),
    -- 候选状态
    merch_candidate INTEGER DEFAULT 0,       -- 文创候选
    evidence_candidate INTEGER DEFAULT 0,    -- 存证候选
    rights_candidate INTEGER DEFAULT 0,      -- 确权候选
    -- AI评估
    ai_score_originality REAL DEFAULT 0 CHECK(ai_score_originality BETWEEN 0 AND 10),    -- 原创性 (0-10)
    ai_score_detail REAL DEFAULT 0 CHECK(ai_score_detail BETWEEN 0 AND 10),              -- 细节丰富度 (0-10)
    ai_score_composition REAL DEFAULT 0 CHECK(ai_score_composition BETWEEN 0 AND 10),    -- 构图能力 (0-10)
    ai_score_expression REAL DEFAULT 0 CHECK(ai_score_expression BETWEEN 0 AND 10),      -- 表达力 (0-10)
    ai_feedback TEXT,             -- AI点评文字
    ai_evaluated_at TEXT,
    -- 蚂蚁链存证
    blockchain_tx_id TEXT,
    blockchain_attested_at TEXT,
    -- 时间
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 作品元数据
CREATE TABLE IF NOT EXISTS work_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id INTEGER NOT NULL UNIQUE REFERENCES works(id),
    prototype_tags_json TEXT,      -- JSON: AI识别出的原型标签
    transform_tags_json TEXT,      -- JSON: AI识别出的变形方法标签
    increase_types_json TEXT,      -- JSON: 增加动作子类型
    color_palette_json TEXT,       -- JSON: 提取的色彩信息
    series_name TEXT DEFAULT '',   -- 系列名称
    module TEXT CHECK(module IN ('A', 'B', NULL)),
    difficulty_assessed INTEGER,   -- AI评估的实际难度
    created_at TEXT DEFAULT (datetime('now'))
);

-- ========================================
-- 4. 展示与成长系统
-- ========================================

-- 展示对象（展馆中的展品）
CREATE TABLE IF NOT EXISTS showcases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_id INTEGER NOT NULL REFERENCES works(id),
    showcase_type TEXT DEFAULT 'personal' CHECK(showcase_type IN ('personal', 'family', 'public')),
    display_order INTEGER DEFAULT 0,
    featured INTEGER DEFAULT 0,   -- 精选
    created_at TEXT DEFAULT (datetime('now'))
);

-- 成长档案
CREATE TABLE IF NOT EXISTS growth_archives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL REFERENCES users(id),
    archive_type TEXT NOT NULL CHECK(archive_type IN ('milestone', 'monthly_report', 'series_collection', 'highlight')),
    title TEXT NOT NULL,
    content_json TEXT,        -- JSON: 档案内容
    cover_work_id INTEGER REFERENCES works(id),
    period_start TEXT,
    period_end TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- ========================================
-- 5. 文创系统
-- ========================================

-- 文创产品类型
CREATE TABLE IF NOT EXISTS merch_types (
    id TEXT PRIMARY KEY,  -- 'photobook', 'sticker', 'tshirt', 'mug', 'canvas', 'postcard', 'tote_bag'
    name_zh TEXT NOT NULL,
    name_en TEXT NOT NULL,
    description TEXT,
    base_price REAL NOT NULL,  -- 基础价格（分）
    preview_template TEXT,     -- 预览模板路径
    is_available INTEGER DEFAULT 1,
    sort_order INTEGER DEFAULT 0
);

-- 文创订单
CREATE TABLE IF NOT EXISTS merch_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER NOT NULL REFERENCES users(id),
    child_id INTEGER NOT NULL REFERENCES users(id),
    merch_type_id TEXT NOT NULL REFERENCES merch_types(id),
    work_ids_json TEXT NOT NULL,    -- JSON: 关联的作品ID列表
    status TEXT DEFAULT 'preview' CHECK(status IN ('preview', 'confirmed', 'paid', 'producing', 'shipped', 'completed', 'cancelled')),
    total_price REAL,
    shipping_address TEXT,
    preview_image_path TEXT,        -- 预览效果图
    tracking_number TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- ========================================
-- 6. 推广系统
-- ========================================

-- 邀请关系
CREATE TABLE IF NOT EXISTS referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inviter_id INTEGER NOT NULL REFERENCES users(id),
    invitee_id INTEGER NOT NULL REFERENCES users(id),
    invite_code TEXT NOT NULL,
    status TEXT DEFAULT 'invited' CHECK(status IN ('invited', 'registered', 'activated', 'first_order', 'rewarded', 'invalid')),
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(invitee_id)  -- 一人只绑定一个邀请人
);

-- 奖励记录
CREATE TABLE IF NOT EXISTS referral_rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    referral_id INTEGER NOT NULL REFERENCES referrals(id),
    reward_type TEXT NOT NULL CHECK(reward_type IN ('register_bonus', 'first_order_bonus', 'revenue_share')),
    recipient_id INTEGER NOT NULL REFERENCES users(id),
    gross_amount REAL DEFAULT 0,
    cost_amount REAL DEFAULT 0,
    net_amount REAL DEFAULT 0,
    reward_amount REAL DEFAULT 0,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'settled', 'invalid', 'reversed')),
    created_at TEXT DEFAULT (datetime('now'))
);

-- ========================================
-- 7. 学币（积分）系统
-- ========================================

-- 学币交易流水
CREATE TABLE IF NOT EXISTS credit_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    amount INTEGER NOT NULL,             -- 正=收入, 负=支出 (单位:学币)
    balance_after INTEGER NOT NULL,      -- 交易后余额
    tx_type TEXT NOT NULL CHECK(tx_type IN (
        'referral_signup',       -- 推荐注册奖励
        'referral_l2_signup',    -- 二级推荐注册奖励
        'welcome_bonus',         -- 被邀请人注册奖励
        'milestone_bonus',       -- 里程碑奖励
        'admin_adjustment',      -- 管理员调整
        'course_purchase',       -- 课程消费
        'merch_purchase',        -- 文创消费
        'withdrawal'             -- 提现
    )),
    reference_id INTEGER,                -- 关联ID（referral_id等）
    description TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- ========================================
-- 索引
-- ========================================
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_user_relations_parent ON user_relations(parent_id);
CREATE INDEX IF NOT EXISTS idx_user_relations_child ON user_relations(child_id);
CREATE INDEX IF NOT EXISTS idx_prototypes_module ON prototypes(module);
CREATE INDEX IF NOT EXISTS idx_prototypes_category ON prototypes(category);
CREATE INDEX IF NOT EXISTS idx_transform_methods_category ON transform_methods(category);
CREATE INDEX IF NOT EXISTS idx_task_templates_module ON task_templates(module);
CREATE INDEX IF NOT EXISTS idx_task_templates_difficulty ON task_templates(difficulty_level);
CREATE INDEX IF NOT EXISTS idx_tasks_child ON tasks(child_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_works_child ON works(child_id);
CREATE INDEX IF NOT EXISTS idx_works_visibility ON works(visibility);
CREATE INDEX IF NOT EXISTS idx_works_created ON works(created_at);
CREATE INDEX IF NOT EXISTS idx_works_merch_candidate ON works(merch_candidate);
CREATE INDEX IF NOT EXISTS idx_work_metadata_work ON work_metadata(work_id);
CREATE INDEX IF NOT EXISTS idx_showcases_work ON showcases(work_id);
CREATE INDEX IF NOT EXISTS idx_showcases_type ON showcases(showcase_type);
CREATE INDEX IF NOT EXISTS idx_growth_archives_child ON growth_archives(child_id);
CREATE INDEX IF NOT EXISTS idx_merch_orders_parent ON merch_orders(parent_id);
CREATE INDEX IF NOT EXISTS idx_merch_orders_status ON merch_orders(status);
CREATE INDEX IF NOT EXISTS idx_referrals_inviter ON referrals(inviter_id);
CREATE INDEX IF NOT EXISTS idx_referrals_code ON referrals(invite_code);
CREATE INDEX IF NOT EXISTS idx_works_task_id ON works(task_id);
CREATE INDEX IF NOT EXISTS idx_works_source_type ON works(source_type);
CREATE INDEX IF NOT EXISTS idx_tasks_template_id ON tasks(template_id);
CREATE INDEX IF NOT EXISTS idx_task_templates_active ON task_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_merch_orders_child ON merch_orders(child_id);
CREATE INDEX IF NOT EXISTS idx_referral_rewards_recipient ON referral_rewards(recipient_id);
CREATE INDEX IF NOT EXISTS idx_work_metadata_module ON work_metadata(module);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user ON credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_type ON credit_transactions(tx_type);
"""
