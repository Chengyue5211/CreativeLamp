"""
绘创前程 — 主应用入口
儿童原创视觉表达成长平台
"""
import os
import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from core.config import BASE_DIR, ENV, IS_PROD
from core.database import init_database

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("huichuang")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("=" * 50)
    logger.info("  绘创前程 — 儿童原创视觉表达成长平台")
    logger.info(f"  环境: {ENV}")
    logger.info("=" * 50)
    init_database()
    logger.info("  数据库初始化完成")
    yield
    logger.info("  绘创前程服务已停止")


app = FastAPI(
    title="绘创前程",
    description="儿童原创视觉表达成长平台 — 没有原型就没有变形，没有变形就没有创造",
    version="0.1.0",
    docs_url=None if IS_PROD else "/docs",
    redoc_url=None if IS_PROD else "/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not IS_PROD else [os.getenv("HC_ALLOWED_ORIGIN", "")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 安全头 + 请求日志中间件
# ============================================================
@app.middleware("http")
async def security_and_logging_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 1)

    # 请求日志
    logger.info(
        f"{request.method} {request.url.path} {response.status_code} {duration}ms"
    )

    # 安全响应头
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if IS_PROD:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            "font-src 'self'; "
            "connect-src 'self'"
        )

    return response


# 静态文件
frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir / "static")), name="static")

# 导入路由
from routers import auth, training, works, showcase, parent, merch, referral, health

app.include_router(health.router)
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(training.router, prefix="/api/training", tags=["训练系统"])
app.include_router(works.router, prefix="/api/works", tags=["作品系统"])
app.include_router(showcase.router, prefix="/api/showcase", tags=["展示系统"])
app.include_router(parent.router, prefix="/api/parent", tags=["家长系统"])
app.include_router(merch.router, prefix="/api/merch", tags=["文创系统"])
app.include_router(referral.router, prefix="/api/referral", tags=["推广系统"])


@app.get("/", response_class=HTMLResponse)
async def index():
    """主页"""
    html_path = BASE_DIR / "frontend" / "templates" / "index.html"
    return html_path.read_text(encoding="utf-8")


@app.get("/api/contours/image/{filename}")
async def contour_image(filename: str):
    """提供轮廓图形的PNG图片"""
    from fastapi.responses import FileResponse
    from fastapi import HTTPException
    # 安全检查：resolve后验证仍在目标目录
    if not filename or "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="非法文件名")
    contour_dir = BASE_DIR / "data" / "contours"
    filepath = (contour_dir / filename).resolve()
    if not str(filepath).startswith(str(contour_dir.resolve())):
        raise HTTPException(status_code=400, detail="非法文件路径")
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="图形不存在")
    return FileResponse(str(filepath), media_type="image/png")


@app.get("/sw.js")
async def service_worker():
    """Service Worker — 必须从根路径提供以获取正确的scope"""
    from fastapi.responses import FileResponse
    sw_path = BASE_DIR / "frontend" / "static" / "sw.js"
    return FileResponse(str(sw_path), media_type="application/javascript")


if __name__ == "__main__":
    import uvicorn
    from core.config import HOST, PORT
    uvicorn.run("main:app", host=HOST, port=PORT, reload=not IS_PROD)
