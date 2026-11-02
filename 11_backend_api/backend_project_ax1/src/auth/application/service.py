from datetime import datetime, timezone

from auth.domain.entities import TokenPayload
from auth.domain.repository import TokenBlacklistRepository
from auth.domain.service import TokenProvider
from shared.core.exceptions import UnauthorizedException
from user.domain.repository import UserRepository
from user.domain.service import PasswordHasher


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        token_blacklist_repo: TokenBlacklistRepository,
        token_provider: TokenProvider,
        password_hasher: PasswordHasher,
    ):
        self._user_repo = user_repository
        self._blacklist_repo = token_blacklist_repo
        self._token_provider = token_provider
        self._password_hasher = password_hasher

    async def login(self, email: str, plain_password: str) -> tuple[str, str, int]:
        """(access_token, token_type, expires_in) 반환"""
        user = await self._user_repo.find_by_email(email)
        if not user or not self._password_hasher.verify(plain_password, user.password_hash):
            raise UnauthorizedException("이메일 또는 비밀번호가 올바르지 않습니다.")

        token, _, _, expires_in = self._token_provider.create_access_token(user.id)
        return token, "bearer", expires_in

    async def logout(self, token: str) -> None:
        payload = self._token_provider.decode_token(token)

        if not await self._blacklist_repo.is_blacklisted(payload.jti):
            await self._blacklist_repo.add(jti=payload.jti, expired_at=payload.exp)

        now = datetime.now(timezone.utc)
        await self._blacklist_repo.cleanup_expired(now)

    async def authenticate_token(self, token: str) -> TokenPayload:
        payload = self._token_provider.decode_token(token)
        if await self._blacklist_repo.is_blacklisted(payload.jti):
            raise UnauthorizedException("로그아웃된 토큰입니다.")
        return payload