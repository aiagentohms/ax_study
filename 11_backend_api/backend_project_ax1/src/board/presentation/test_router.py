from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from board.infrastructure.models import Board, Post
from shared.core.database import get_db
from shared.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/test")

@router.get("/1")
async def test1(session: AsyncSession = Depends(get_db)):
    board = Board(
        id="qna",
        name="제목1"  
    )

    session.add(board)

    for i in range(1, 6):
        item = Post(
            title=f"제목{i}",
            content=f"내용{i}",
            board_config=board  
        )
        session.add(item)

    await session.commit()
    await session.refresh(board)

@router.get("/2")
async def test2(session: AsyncSession = Depends(get_db)):
    # 수정을 하려면 불러와야 합니다.
    # get(..) - 1차 캐리, 한번 조회 후에는 메모리에서 직접 가져온다.
    board = await session.get(Board, "qna")
    logger.info(f"board={board.id}, name={board.name}, created_at={board.created_at}")

# 모델 객체는 변화 감지를 한다(Dirty Checking). - 수정 -> UPDATE

    board.name = '수정' + board.name

    await session.commit()
    await session.refresh(board) # DB 변경 사항을 기존 모델 객체에 반영

    logger.info(f"id=board={board.id}, name={board.name}, created_at={board.created_at}, modified_at={board.modified_at}")

@router.get("/3")
async def test2(session: AsyncSession = Depends(get_db)):
    board = await session.get(Board, "qna")
    await session.delete(board)
    await session.commit()

@router.get("/4")
async def test2(session: AsyncSession = Depends(get_db)):
    # stmt = select(Post).where(Post.board_id == 'qua')
    stmt = (
            select(Post)
            .options(joinedload(Post.board_config))
            .where(Post.board_id == 'qua')
    )
    items = await session.scalars(stmt)

    return [(i.to_dict(), i.board_config.to_dict()) for i in items]

@router.get("/5")
async def test2(session: AsyncSession = Depends(get_db)):
    stmt = (select(Board)
            .options(selectinload(Board.posts))
            .where(Board.id == "qna")
        )

    board = await session.scalar(stmt)
    logger.info(f"board: {board.to_dict()}")

    return [post.to_dict() for post in board.posts]
