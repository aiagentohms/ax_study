from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from assignment.domain import (
    ActiveLoanNotFoundError,
    AlreadyBorrowedError,
    BookUnavailableError,
    DuplicateBookError,
    InactiveMemberError,
    LoanLimitError,
    Member,
)
from assignment.service import LibraryService
from assignment.storage import JsonRepository


class LibraryServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.data_path = Path(self.temporary_directory.name) / "library.json"
        self.service = LibraryService(JsonRepository(self.data_path))
        self.service.add_book("978-1-234", "파이썬 기초", "홍길동")
        self.service.add_member("member-1", "김회원")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_borrow_and_return_updates_availability(self) -> None:
        loan = self.service.borrow_book(
            "9781234", "member-1", borrowed_on=date(2026, 9, 1)
        )
        self.assertEqual(loan.due_on, date(2026, 9, 15))
        self.assertEqual(self.service.available_copies("9781234"), 0)

        receipt = self.service.return_book(
            "9781234", "member-1", returned_on=date(2026, 9, 15)
        )
        self.assertEqual(receipt.overdue_days, 0)
        self.assertEqual(self.service.available_copies("9781234"), 1)

    def test_overdue_days_are_reported(self) -> None:
        self.service.borrow_book(
            "9781234", "member-1", borrowed_on=date(2026, 9, 1), loan_days=7
        )
        receipt = self.service.return_book(
            "9781234", "member-1", returned_on=date(2026, 9, 11)
        )
        self.assertEqual(receipt.overdue_days, 3)

    def test_unavailable_book_cannot_be_borrowed(self) -> None:
        self.service.add_member("member-2", "이회원")
        self.service.borrow_book("9781234", "member-1")
        with self.assertRaises(BookUnavailableError):
            self.service.borrow_book("9781234", "member-2")

    def test_same_member_cannot_borrow_same_isbn_twice(self) -> None:
        self.service.add_book("two-copies", "두 권짜리", "작가", 2)
        self.service.borrow_book("two-copies", "member-1")
        with self.assertRaises(AlreadyBorrowedError):
            self.service.borrow_book("two-copies", "member-1")

    def test_member_loan_limit_is_enforced(self) -> None:
        self.service.add_member("limited", "한권만", max_loans=1)
        self.service.add_book("book-2", "두 번째 책", "작가")
        self.service.borrow_book("9781234", "limited")
        with self.assertRaises(LoanLimitError):
            self.service.borrow_book("book-2", "limited")

    def test_inactive_member_cannot_borrow(self) -> None:
        self.service.state.members["member-1"] = Member(
            member_id="member-1", name="김회원", active=False
        )
        with self.assertRaises(InactiveMemberError):
            self.service.borrow_book("9781234", "member-1")

    def test_return_requires_matching_active_loan(self) -> None:
        with self.assertRaises(ActiveLoanNotFoundError):
            self.service.return_book("9781234", "member-1")

    def test_duplicate_isbn_is_rejected_after_normalization(self) -> None:
        with self.assertRaises(DuplicateBookError):
            self.service.add_book("978 1 234", "중복", "작가")

    def test_state_survives_repository_reload(self) -> None:
        self.service.borrow_book("9781234", "member-1")
        reloaded = LibraryService(JsonRepository(self.data_path))
        self.assertEqual(reloaded.available_copies("9781234"), 0)
        self.assertEqual(len(reloaded.list_loans()), 1)
        with self.data_path.open(encoding="utf-8") as file:
            self.assertEqual(json.load(file)["schema_version"], 1)

    def test_search_matches_title_author_and_isbn(self) -> None:
        self.assertEqual(len(self.service.search_books("파이썬")), 1)
        self.assertEqual(len(self.service.search_books("홍길동")), 1)
        self.assertEqual(len(self.service.search_books("9781234")), 1)


if __name__ == "__main__":
    unittest.main()
