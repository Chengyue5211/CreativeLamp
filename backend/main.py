"""
绘创前程 — 主应用入口
儿童原创视觉表达成长平台
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from core.config import BASE_DIR, ENV, IS_PROD
from core.database import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("=" * 50)
    print("  绘创前程 — 儿童原创视觉表达成长平台")
    print(f"  环境: {ENV}")
    print("=" * 50)
    init_database()
    print("  数据库初始化完成")
    yield
    # 关闭时
    print("  绘创前程服务已停止")


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


if __name__ == "__main__":
    import uvicorn
    from core.config import HOST, PORT
    uvicorn.run("main:app", host=HOST, port=PORT, reload=not IS_PROD)
