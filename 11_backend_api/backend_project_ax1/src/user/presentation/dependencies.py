from user.application.service import UserService
from user.domain.repository import UserRepository


def provide_user_service() -> UserService:
    """FastAPI Depends 플레이스홀더 (container.py에서 바인딩)"""
    raise NotImplementedError("UserService 의존성이 주입되지 않았습니다.")


def provide_user_repository() -> UserRepository:
    """FastAPI Depends 플레이스홀더 (container.py에서 바인딩)"""
    raise NotImplementedError("UserRepository 의존성이 주입되지 않았습니다.")