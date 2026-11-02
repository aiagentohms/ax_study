import os
import uuid
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt

from auth.domain.entities import TokenPayload
from auth.domain.service import TokenProvider
from shared.core.exceptions import UnauthorizedException

class JwtTokenProvider(TokenProvider):
    def __init__(
        self,
        # HS512 권장 규격에 맞춰 최소 64바이트(512비트) 이상의 시크릿 키 권장
        secret_key: str = os.getenv("JWT_SECRET_KEY", "your-at-least-64-bytes-long-super-secure-secret-key-for-hs512-algorithm-safety!"),
        algorithm: str = "HS512",
        access_token_expire_minutes: int = 60,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = access_token_expire_minutes

    def create_access_token(self, user_id: uuid.UUID) -> tuple[str, str, datetime, int]:
        now = datetime.now(timezone.utc)
        expires_delta = timedelta(minutes=self.expire_minutes)
        expired_at = now + expires_delta
        expires_in = int(expires_delta.total_seconds())
        jti = str(uuid.uuid4())

        payload = {
            "sub": str(user_id),
            "jti": jti,
            "exp": expired_at,
            "iat": now,
        }
        encoded_jwt = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt, jti, expired_at, expires_in

    def decode_token(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return TokenPayload(
                user_id=uuid.UUID(payload["sub"]),
                jti=payload["jti"],
                exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            )
        except (jwt.PyJWTError, KeyError, ValueError):
            raise UnauthorizedException("유효하지 않거나 만료된 토큰입니다.")