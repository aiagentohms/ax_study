from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


class LibraryError(Exception):
    """사용자에게 그대로 안내할 수 있는 도서관 업무 오류."""


class DuplicateBookError(LibraryError):
    pass


class DuplicateMemberError(LibraryError):
    pass


class BookNotFoundError(LibraryError):
    pass


class MemberNotFoundError(LibraryError):
    pass


class BookUnavailableError(LibraryError):
    pass


class AlreadyBorrowedError(LibraryError):
    pass


class LoanLimitError(LibraryError):
    pass


class ActiveLoanNotFoundError(LibraryError):
    pass


class InactiveMemberError(LibraryError):
    pass


@dataclass(frozen=True, slots=True)
class Book:
    isbn: str
    title: str
    author: str
    total_copies: int = 1


@dataclass(frozen=True, slots=True)
class Member:
    member_id: str
    name: str
    max_loans: int = 5
    active: bool = True


@dataclass(slots=True)
class Loan:
    loan_id: str
    isbn: str
    member_id: str
    borrowed_on: date
    due_on: date
    returned_on: date | None = None

    @property
    def is_active(self) -> bool:
        return self.returned_on is None


@dataclass(slots=True)
class LibraryState:
    books: dict[str, Book] = field(default_factory=dict)
    members: dict[str, Member] = field(default_factory=dict)
    loans: list[Loan] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class BookAvailability:
    book: Book
    available_copies: int


@dataclass(frozen=True, slots=True)
class ReturnReceipt:
    loan: Loan
    overdue_days: int
