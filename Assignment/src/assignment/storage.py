from __future__ import annotations

import json
import os
import tempfile
from datetime import date
from pathlib import Path

from .domain import Book, LibraryState, Loan, Member


class JsonRepository:
    """한 번의 파일 교체로 상태를 저장하는 간단한 JSON 저장소."""

    SCHEMA_VERSION = 1

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self) -> LibraryState:
        if not self.path.exists():
            return LibraryState()

        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        version = data.get("schema_version")
        if version != self.SCHEMA_VERSION:
            raise ValueError(f"지원하지 않는 데이터 스키마 버전입니다: {version}")

        books = {
            item["isbn"]: Book(
                isbn=item["isbn"],
                title=item["title"],
                author=item["author"],
                total_copies=item["total_copies"],
            )
            for item in data.get("books", [])
        }
        members = {
            item["member_id"]: Member(
                member_id=item["member_id"],
                name=item["name"],
                max_loans=item["max_loans"],
                active=item["active"],
            )
            for item in data.get("members", [])
        }
        loans = [
            Loan(
                loan_id=item["loan_id"],
                isbn=item["isbn"],
                member_id=item["member_id"],
                borrowed_on=date.fromisoformat(item["borrowed_on"]),
                due_on=date.fromisoformat(item["due_on"]),
                returned_on=(
                    date.fromisoformat(item["returned_on"])
                    if item.get("returned_on")
                    else None
                ),
            )
            for item in data.get("loans", [])
        ]
        return LibraryState(books=books, members=members, loans=loans)

    def save(self, state: LibraryState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": self.SCHEMA_VERSION,
            "books": [
                {
                    "isbn": book.isbn,
                    "title": book.title,
                    "author": book.author,
                    "total_copies": book.total_copies,
                }
                for book in sorted(state.books.values(), key=lambda item: item.isbn)
            ],
            "members": [
                {
                    "member_id": member.member_id,
                    "name": member.name,
                    "max_loans": member.max_loans,
                    "active": member.active,
                }
                for member in sorted(
                    state.members.values(), key=lambda item: item.member_id
                )
            ],
            "loans": [
                {
                    "loan_id": loan.loan_id,
                    "isbn": loan.isbn,
                    "member_id": loan.member_id,
                    "borrowed_on": loan.borrowed_on.isoformat(),
                    "due_on": loan.due_on.isoformat(),
                    "returned_on": (
                        loan.returned_on.isoformat() if loan.returned_on else None
                    ),
                }
                for loan in state.loans
            ],
        }

        temporary_name: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temporary_name = temporary.name
                json.dump(payload, temporary, ensure_ascii=False, indent=2)
                temporary.write("\n")
                temporary.flush()
                os.fsync(temporary.fileno())
            os.replace(temporary_name, self.path)
        finally:
            if temporary_name and os.path.exists(temporary_name):
                os.unlink(temporary_name)
