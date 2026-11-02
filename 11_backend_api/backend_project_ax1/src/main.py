from contextlib import asynccontextmanager
from fastapi import FastAPI
from container import wire_dependencies
from shared.core.database import close_db, engine
from shared.core.exception_handlers import register_exception_handlers
from shared.core.models import init_models
from shared.core.logger import get_logger
from shared.core.models import Base
from user.presentation.routers.v1.router import router as user_router
from auth.presentation.routers.v1.router import router as auth_router
from board.presentation.test_router import router as test_router

logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("애플리케이션 시작, 모델 초기화 및 DB 스키마 확인 중...")
    init_models()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("애플리케이션 준비 완료.")
    yield

    logger.info("애플리케이션 종료 처리 중...")
    await close_db()


app = FastAPI(
    title="쇼핑몰 API",
    description="쇼핑몰 백엔드 API 서비스",
    version="1.0.0",
    lifespan=lifespan,
)

# 전역 예외 핸들러 바인딩
register_exception_handlers(app)

# 의존성 주입 일괄 바인딩
wire_dependencies(app)

# 라우터 등록
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(test_router)