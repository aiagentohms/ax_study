from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.application.service import AuthService
from shared.core.exceptions import ForbiddenException, UnauthorizedException
from user.domain.repository import UserRepository
from user.domain.user import User
from user.presentation.dependencies import provide_user_repository

security = HTTPBearer(auto_error=True)

def provide_auth_service() -> AuthService:
    raise NotImplementedError("AuthService 의존성이 주입되지 않았습니다.")


async def get_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        auth_service: Annotated[AuthService, Depends(provide_auth_service)],
        user_repo: Annotated[UserRepository, Depends(provide_user_repository)]
) -> User:
    """인증된 현재 사용자 반환"""
    token = credentials.credentials
    payload = await auth_service.authenticate_token(token)
    user = await user_repo.get_by_id(payload.user_id)

    if not user:
        raise UnauthorizedException("존재하지 않는 사용자입니다.")

    if user.resign:
        raise ForbiddenException(
            message="탈퇴한 회원은 서비스를 이용할 수 없습니다.",
            error_code="USER_ALREADY_WITHDRAWN",
        )

    return user

async def require_admin(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """관리자 권한 인가 체크"""
    if current_user.role != "ADMIN":
        raise ForbiddenException(
            message="관리자 권한이 필요합니다.",
            error_code="ADMIN_PERMISSION_DENIED",
        )
    return current_user