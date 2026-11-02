from fastapi import APIRouter

router = APIRouter(prefix="/v1/order", tags=["주문"])


@router.get("")
asunc def test1():
    return {"message": "테스트1"}

@router.get("/test")
async def test2():
    return {"message": "테스트2"}