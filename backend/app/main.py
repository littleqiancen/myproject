import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_v1_router
from app.config import get_settings
from app.database import engine
from app.models import Base

settings = get_settings()

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 关闭时释放引擎
    await engine.dispose()


app = FastAPI(
    title="AI测试用例生成平台",
    description="基于AI的PRD文档 → 测试点 → 测试用例 生成平台",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_v1_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
