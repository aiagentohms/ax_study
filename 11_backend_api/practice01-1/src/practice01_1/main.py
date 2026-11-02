import asyncio
import logging
from contextlib import asynccontextmanager, suppress
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

# 현재 파일 위치를 기준으로 프로젝트 최상위 폴더를 찾습니다.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# 프로젝트 최상위의 .env 파일을 읽습니다.
load_dotenv(PROJECT_ROOT / ".env", override=True)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "")
ACCESS_TOKEN_EXPIRE_SECONDS = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", "300")
)

# 설정이 잘못된 상태에서는 서버 실행을 중단합니다.
if len(JWT_SECRET_KEY) < 32:
    raise RuntimeError("JWT_SECRET_KEY를 충분한 길이의 비밀키로 설정하세요.")

if JWT_ALGORITHM != "HS256":
    raise RuntimeError("이번 실습의 JWT_ALGORITHM은 HS256이어야 합니다.")

if ACCESS_TOKEN_EXPIRE_SECONDS <= 0:
    raise RuntimeError("토큰 유효기간은 0보다 커야 합니다.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("practice.auth")
logger.info("적용된 토큰 유효기간: %d초", ACCESS_TOKEN_EXPIRE_SECONDS)

# 토큰 고유 ID -> 만료 시각
token_blacklist: dict[str, float] = {}

CLEANUP_INTERVAL_SECONDS = 30

async def cleanup_expired_tokens():
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)

        now = datetime.now(timezone.utc).timestamp()

        expired_ids = [
            token_id
            for token_id, expires_at in token_blacklist.items()
            if expires_at <= now
        ]

        for token_id in expired_ids:
            del token_blacklist[token_id]

        logger.info(
            "블랙리스트 정리: 삭제 %d건, 남은 %d건",
            len(expired_ids),
            len(token_blacklist),
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_task = asyncio.create_task(cleanup_expired_tokens())
    logger.info("블랙리스트 정리 작업 시작: 30초 간격")

    try:
        yield
    finally:
        cleanup_task.cancel()

        with suppress(asyncio.CancelledError):
            await cleanup_task

        logger.info("블랙리스트 정리 작업 종료")

app = FastAPI(
    title="로그아웃 API 실습",
    description="JWT 검증과 블랙리스트 기반 로그아웃을 연습합니다.",
    version="0.1.0",
    lifespan=lifespan,
)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


@app.get("/", summary="서버 연결 확인")
async def root():
    return {
        "message": "로그아웃 API 실습 서버가 실행 중입니다.",
        "project": "practice01-1",
    }


@app.post(
    "/auth/token",
    response_model=TokenResponse,
    tags=["인증"],
    summary="실습용 토큰 발급",
    description="회원 인증 없이 고정된 실습 사용자의 토큰을 발급합니다.",
)

async def issue_practice_token():
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        seconds=ACCESS_TOKEN_EXPIRE_SECONDS
    )

    payload = {
        "sub": "practice-user",
        "jti": str(uuid4()),
        "iat": now,
        "exp": expires_at,
    }

    access_token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_SECONDS,
    )

bearer_schmeme = HTTPBearer(auto_error=False)



async def verify_access_token(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_schmeme),
) -> dict:
    authentication_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 헤더가 없거나 Bearer 형식이 아니면 거절합니다.
    if credentials is None:
        raise authentication_error

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=["HS256"],
            options={
                "require": ["sub", "jti", "iat", "exp"],
            },
        )
    except jwt.InvalidTokenError:
        # 위변조, 만료, 필수 정보 누락 등을 같은 응답으로 처리합니다.
        raise authentication_error from None

    # 사용자 ID와 토큰 ID는 비어 있지 않은 문자열이어야 합니다.
    for field in ("sub", "jti"):
        if not isinstance(payload[field], str) or not payload[field].strip():
            raise authentication_error

    # 서명과 만료 검증을 통과했어도 로그아웃한 토큰이면 거절합니다.
    if payload["jti"] in token_blacklist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이미 로그아웃된 토큰입니다. 다시 로그인해 주세요.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

class MeResponse(BaseModel):
    user_id: str
    token_id: str

@app.get(
    "/auth/me",
    response_model=MeResponse,
    tags=["인증"],
    summary="토큰 검증 및 실습 사용자 확인",
)
async def get_me(payload: dict = Depends(verify_access_token)):
    return MeResponse(
        user_id=payload["sub"],
        token_id=payload["jti"],
    )

@app.post(
    "/auth/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    tags=["인증"],
    summary="로그아웃 및 토큰 무효화",
)

async def logout(payload: dict = Depends(verify_access_token)):
    token_id = payload["jti"]
    expires_at = float(payload["exp"])

    token_blacklist[token_id] = expires_at

    remaining_seconds = max(
        0,
        expires_at - datetime.now(timezone.utc).timestamp(),
    )

    logger.info(
        "블랙리스트 등록 완료: 현재 %d건, 방금 등록한 토큰 만료까지 약 %.1f초",
        len(token_blacklist),
        remaining_seconds,
    )   

    return Response(status_code=status.HTTP_204_NO_CONTENT)