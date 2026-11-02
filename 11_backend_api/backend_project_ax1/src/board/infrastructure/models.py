from datetime import datetime, timezone
from sqlalchemy import String, Text, BigInteger, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.core.models import Base

class Board(Base):
    """게시판 설정"""
    __tablename__ = "boards"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(65), nullable=False)
    write_role: Mapped[str] = mapped_column(String(30), default="ALL", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.now(timezone.utc), 
        nullable=False
    )

    modified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), 
        nullable=True, 
        onupdate=datetime.now(timezone.utc)
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    """
    lazy: raise 기본값, 가져오지 않음
            selectin : 1:N -> 1차 쿼리 -> in 조건으로 2차 쿼리 수행
            joined : N:1 -> 처음부터 LEF JOIN
    """

    posts: Mapped[list["Post"]] = relationship(
        back_populates="board_config",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True, 
        autoincrement=True
    )

    category: Mapped[str] = mapped_column(
        String(60),
        nullable=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.now(timezone.utc), 
        nullable=False
    )

    modified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), 
        nullable=True, 
        onupdate=datetime.now(timezone.utc)
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # 외래키
    board_id: Mapped[str] = mapped_column(
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # 게시판 설정(N:1)
    board_config: Mapped["Board"] = relationship(
        back_populates="posts",
        lazy="joined"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content
        }