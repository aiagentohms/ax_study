import time
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# 1. OAuth2 스키마 및 라우터 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")
router = APIRouter(prefix="/v1/auth", tags=["Auth"])

SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"

# 2. 블랙리스트를 딕셔너리 형태로 선언 { 토큰문자열: 만료시간(timestamp) }
LOGOUT_BLACKLIST: dict[str, float] = {}


# 3. 주기적으로 실행할 블랙리스트 청소 함수
def cleanup_blacklist():
    """
    현재 시간 기준으로 이미 JWT 유효기간이 지나 자연 만료된 토큰들을
    서버 메모리(LOGOUT_BLACKLIST)에서 영구 삭제합니다.
    """
    current_time = time.time()
    # 만료 시간이 지난 토큰들의 키값만 추출
    expired_tokens = [
        token for token, exp_time in LOGOUT_BLACKLIST.items() if current_time > exp_time
    ]
    
    # 메모리에서 제거
    for token in expired_tokens:
        del LOGOUT_BLACKLIST[token]
        
    if expired_tokens:
        print(f"[메모리 청소] 만료된 토큰 {len(expired_tokens)}개를 블랙리스트에서 제거했습니다.")


# 4. 공통 의존성: 토큰 검증 및 블랙리스트 체크
async def get_current_user_and_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 자격 증명을 검증할 수 없습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # [검증 1] 이미 로그아웃 처리되어 블랙리스트에 존재하는 토큰인지 확인
    if token in LOGOUT_BLACKLIST:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이미 로그아웃된 토큰입니다. 다시 로그인해 주세요."
        )
        
    try:
        # [검증 2] JWT 자체 유효성 및 만료 시간(exp) 디코딩 검사
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        exp_time: float = payload.get("exp") # 토큰의 만료 타임스탬프
        
        if user_id is None or exp_time is None:
            raise credentials_exception
            
        # 이후 로직에서 사용할 수 있도록 유저ID, 토큰, 만료시간을 함께 반환
        return {"user_id": user_id, "token": token, "exp": exp_time}
        
    except JWTError:
        raise credentials_exception


# 5. 로그아웃 엔드포인트
@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    background_tasks: BackgroundTasks,
    auth_data: dict = Depends(get_current_user_and_token)
):
    """
    로그아웃 요청 시 토큰을 블랙리스트에 등록하고, Backgroud Task로 메모리를 청소합니다.
    """
    target_token = auth_data["token"]
    token_exp = auth_data["exp"]
    
    # [핵심] 블랙리스트에 토큰과 해당 토큰의 만료 시간을 함께 기록
    LOGOUT_BLACKLIST[target_token] = token_exp
    print(f"사용자 {auth_data['user_id']} 로그아웃 완료. 토큰이 블랙리스트에 등록되었습니다.")
    
    # [효율성] 백그라운드 태스크를 통해 클라이언트 응답에 방해를 주지 않고 메모리 청소기 가동
    background_tasks.add_task(cleanup_blacklist)
    
    return
