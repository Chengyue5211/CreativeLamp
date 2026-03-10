"""
绘创前程 — 全局配置
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent.parent

# 环境
ENV = os.getenv("HC_ENV", "development")  # development / production
IS_PROD = ENV == "production"

# 服务器
HOST = os.getenv("HC_HOST", "0.0.0.0")
PORT = int(os.getenv("HC_PORT", "8100"))

# 数据目录
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
THUMBNAIL_DIR = DATA_DIR / "thumbnails"
PRINTABLE_DIR = DATA_DIR / "printables"
MERCH_PREVIEW_DIR = DATA_DIR / "merch_previews"

# AI 配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")

# 上传限制
MAX_UPLOAD_SIZE_MB = 10
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

# 创建必要目录
for d in [DATA_DIR, UPLOAD_DIR, THUMBNAIL_DIR, PRINTABLE_DIR, MERCH_PREVIEW_DIR]:
    d.mkdir(parents=True, exist_ok=True)
