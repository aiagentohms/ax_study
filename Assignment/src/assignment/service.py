from __future__ import annotations

from datetime import date, timedelta
from uuid import uuid4

from .domain import (
    ActiveLoanNotFoundError,
    AlreadyBorrowedError,
    Book,
    BookAvailability,
    BookNotFoundError,
    BookUnavailableError,
    DuplicateBookError,
    DuplicateMemberError,
    InactiveMemberError,
    Loan,
    LoanLimitError,
    Member,
    MemberNotFoundError,
    ReturnReceipt,
)
from .storage import JsonRepository


def _required(value: str, label: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{label}은(는) 비워 둘 수 없습니다.")
    return normalized


def normalize_isbn(value: str) -> str:
    normalized = value.replace("-", "").replace(" ", "").upper()
    return _required(normalized, "ISBN")


class LibraryService:
    DEFAULT_LOAN_DAYS = 14

    def __init__(self, repository: JsonRepository):
        self.repository = repository
        self.state = repository.load()

    def add_book(
        self, isbn: str, title: str, author: str, total_copies: int = 1
    ) -> Book:
        isbn = normalize_isbn(isbn)
        title = _required(title, "도서명")
        author = _required(author, "저자")
        if total_copies < 1:
            raise ValueError("보유 권수는 1 이상이어야 합니다.")
        if isbn in self.state.books:
            raise DuplicateBookError(f"이미 등록된 ISBN입니다: {isbn}")

        book = Book(
            isbn=isbn, title=title, author=author, total_copies=total_copies
        )
        self.state.books[isbn] = book
        self.repository.save(self.state)
        return book

    def add_member(
        self, member_id: str, name: str, max_loans: int = 5
    ) -> Member:
        member_id = _required(member_id, "회원 ID")
        name = _required(name, "회원명")
        if max_loans < 1:
            raise ValueError("대출 한도는 1 이상이어야 합니다.")
        if member_id in self.state.members:
            raise DuplicateMemberError(f"이미 등록된 회원 ID입니다: {member_id}")

        member = Member(member_id=member_id, name=name, max_loans=max_loans)
        self.state.members[member_id] = member
        self.repository.save(self.state)
        return member

    def search_books(self, query: str = "") -> list[BookAvailability]:
        query = query.strip().casefold()
        result = []
        for book in self.state.books.values():
            searchable = f"{book.isbn} {book.title} {book.author}".casefold()
            if query and query not in searchable:
                continue
            result.append(
                BookAvailability(
                    book=book,
                    available_copies=self.available_copies(book.isbn),
                )
            )
        return sorted(result, key=lambda item: (item.book.title, item.book.isbn))

    def list_loans(self, active_only: bool = True) -> list[Loan]:
        loans = (
            [loan for loan in self.state.loans if loan.is_active]
            if active_only
            else list(self.state.loans)
        )
        return sorted(loans, key=lambda loan: (loan.due_on, loan.loan_id))

    def available_copies(self, isbn: str) -> int:
        isbn = normalize_isbn(isbn)
        book = self.state.books.get(isbn)
        if book is None:
            raise BookNotFoundError(f"등록되지 않은 도서입니다: {isbn}")
        active_count = sum(
            loan.is_active and loan.isbn == isbn for loan in self.state.loans
        )
        return book.total_copies - active_count

    def borrow_book(
        self,
        isbn: str,
        member_id: str,
        *,
        borrowed_on: date | None = None,
        loan_days: int = DEFAULT_LOAN_DAYS,
    ) -> Loan:
        isbn = normalize_isbn(isbn)
        member_id = _required(member_id, "회원 ID")
        if loan_days < 1:
            raise ValueError("대출 기간은 1일 이상이어야 합니다.")

        if isbn not in self.state.books:
            raise BookNotFoundError(f"등록되지 않은 도서입니다: {isbn}")
        member = self.state.members.get(member_id)
        if member is None:
            raise MemberNotFoundError(f"등록되지 않은 회원입니다: {member_id}")
        if not member.active:
            raise InactiveMemberError(f"대출이 정지된 회원입니다: {member_id}")

        member_loans = [
            loan
            for loan in self.state.loans
            if loan.is_active and loan.member_id == member_id
        ]
        if any(loan.isbn == isbn for loan in member_loans):
            raise AlreadyBorrowedError("같은 회원이 이미 이 도서를 대출 중입니다.")
        if len(member_loans) >= member.max_loans:
            raise LoanLimitError(
                f"회원의 대출 한도({member.max_loans}권)에 도달했습니다."
            )
        if self.available_copies(isbn) < 1:
            raise BookUnavailableError("현재 대출 가능한 도서가 없습니다.")

        borrowed_on = borrowed_on or date.today()
        loan = Loan(
            loan_id=uuid4().hex,
            isbn=isbn,
            member_id=member_id,
            borrowed_on=borrowed_on,
            due_on=borrowed_on + timedelta(days=loan_days),
        )
        self.state.loans.append(loan)
        self.repository.save(self.state)
        return loan

    def return_book(
        self,
        isbn: str,
        member_id: str,
        *,
        returned_on: date | None = None,
    ) -> ReturnReceipt:
        isbn = normalize_isbn(isbn)
        member_id = _required(member_id, "회원 ID")
        if isbn not in self.state.books:
            raise BookNotFoundError(f"등록되지 않은 도서입니다: {isbn}")
        if member_id not in self.state.members:
            raise MemberNotFoundError(f"등록되지 않은 회원입니다: {member_id}")

        loan = next(
            (
                item
                for item in self.state.loans
                if item.is_active
                and item.isbn == isbn
                and item.member_id == member_id
            ),
            None,
        )
        if loan is None:
            raise ActiveLoanNotFoundError(
                "해당 회원의 활성 대출 기록을 찾을 수 없습니다."
            )

        returned_on = returned_on or date.today()
        if returned_on < loan.borrowed_on:
            raise ValueError("반납일은 대출일보다 빠를 수 없습니다.")
        loan.returned_on = returned_on
        overdue_days = max((returned_on - loan.due_on).days, 0)
        self.repository.save(self.state)
        return ReturnReceipt(loan=loan, overdue_days=overdue_days)
