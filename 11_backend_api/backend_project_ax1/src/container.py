from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from auth.application.service import AuthService
from auth.domain.service import TokenProvider
from auth.infrastructure.repositories import SqlAlchemyTokenBlacklistRepository
from auth.infrastructure.security import JwtTokenProvider
from auth.presentation.dependencies import provide_auth_service
from shared.core.database import get_db
from user.application.service import UserService
from user.domain.repository import UserRepository
from user.infrastructure.repositories import SqlAlchemyUserRepository
from user.infrastructure.security import BcryptPasswordHasher
from user.presentation.dependencies import (
    provide_user_repository,
    provide_user_service,
)

# 싱글턴 유틸리티 인스턴스 
_password_hasher = BcryptPasswordHasher()
_token_provider: TokenProvider = JwtTokenProvider()


# User 도메인
def create_user_repository(
    session: AsyncSession = Depends(get_db),
) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def create_user_service(
    repository: UserRepository = Depends(create_user_repository),
) -> UserService:
    return UserService(
        repository=repository,
        hasher=_password_hasher,
    )


# Auth 도메인
def create_auth_service(
    session: AsyncSession = Depends(get_db),
    user_repository: UserRepository = Depends(create_user_repository),
) -> AuthService:
    blacklist_repository = SqlAlchemyTokenBlacklistRepository(session)
    return AuthService(
        user_repository=user_repository,
        token_blacklist_repo=blacklist_repository,
        token_provider=_token_provider,
        password_hasher=_password_hasher,
    )

# FastAPI Dependency Overrides 와이어링
def wire_dependencies(app: FastAPI) -> None:
    app.dependency_overrides.update(
        {
            provide_user_repository: create_user_repository,
            provide_user_service: create_user_service,
            provide_auth_service: create_auth_service,
        }
    )