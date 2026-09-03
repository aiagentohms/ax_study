from __future__ import annotations

import unittest
from unittest.mock import patch

from main import Library, create_book_from_input
from models import Book, Ebook, Novel


class AssignmentRequirementsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.library = Library()
        self.book = Book("파이썬 기초", "홍길동", "111", 2026)
        self.library.add_book(self.book)

    def test_duplicate_isbn_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.library.add_book(Book("중복", "작가", "111", 2025))

    def test_blank_book_fields_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Book(" ", "작가", "222", 2025)

    def test_dictionary_and_set_track_books(self) -> None:
        self.assertIs(self.library.books["111"], self.book)
        self.assertIn("111", self.library.book_ids)

    def test_borrow_and_return_record_tuple_history(self) -> None:
        self.library.borrow_book("111")
        self.assertTrue(self.book.is_borrowed)
        self.assertIsInstance(self.library.history[0], tuple)
        self.library.return_book("111")
        self.assertFalse(self.book.is_borrowed)
        self.assertEqual([item[1] for item in self.library.history], ["대여", "반납"])

    def test_invalid_state_transitions_raise(self) -> None:
        with self.assertRaises(ValueError):
            self.library.return_book("111")
        self.library.borrow_book("111")
        with self.assertRaises(ValueError):
            self.library.borrow_book("111")

    def test_search_filters_multiple_fields(self) -> None:
        self.assertEqual(self.library.search_books("파이썬"), [self.book])
        self.assertEqual(self.library.search_books("홍길동"), [self.book])
        self.assertEqual(self.library.search_books("111"), [self.book])

    def test_subclasses_override_details(self) -> None:
        novel = Novel("소설", "작가", "222", 2024, "추리")
        ebook = Ebook("전자책", "작가", "333", 2025, 12.5, "EPUB")
        self.assertIn("장르: 추리", novel.get_details())
        self.assertIn("12.5MB EPUB", ebook.get_details())

    def test_statistics_count_loans_and_rank_books(self) -> None:
        self.library.borrow_book("111")
        monthly, ranking = self.library.statistics()
        self.assertEqual(sum(monthly.values()), 1)
        self.assertEqual(ranking[0], self.book)

    @patch("builtins.input", side_effect=["3", "전자책", "작가", "333", "2026", "5.5", "PDF"])
    def test_validated_input_creates_specialized_book(self, _mock_input) -> None:
        book = create_book_from_input()
        self.assertIsInstance(book, Ebook)


if __name__ == "__main__":
    unittest.main()
