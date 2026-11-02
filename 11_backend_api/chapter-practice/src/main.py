from fastapi import FastAPI
from src.auth import router as auth_router  # auth.py에서 라우터 가져오기

app = FastAPI(title="Practice API")

# /v1/auth/logout 주소로 매핑되도록 라우터 등록
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "서버가 정상적으로 작동 중입니다."}
