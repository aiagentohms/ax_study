from __future__ import annotations

from collections import Counter
from datetime import datetime

from models import Book, Ebook, Novel
from utils import float_input, format_time, integer_input, required_input, timestamp


class Library:
    """도서 자료구조와 대여·반납 규칙을 관리한다."""

    def __init__(self) -> None:
        # ISBN 조회가 잦으므로 순차 탐색 리스트 대신 딕셔너리를 사용한다.
        self.books: dict[str, Book] = {}
        # 집합은 ISBN 중복 확인 의도를 드러내며 평균적으로 빠르게 검사한다.
        self.book_ids: set[str] = set()
        # 변경할 수 없는 튜플을 리스트에 쌓아 발생 순서를 보존한다.
        self.history: list[tuple[datetime, str, str]] = []
        self.error_logs: list[tuple[datetime, str, str]] = []

    def add_book(self, book: Book) -> None:
        if book.isbn in self.book_ids:
            raise ValueError(f"이미 등록된 ISBN입니다: {book.isbn}")
        self.books[book.isbn] = book
        self.book_ids.add(book.isbn)

    def list_books(self) -> list[Book]:
        return sorted(self.books.values(), key=lambda book: (book.title, book.isbn))

    def search_books(self, keyword: str) -> list[Book]:
        keyword = keyword.strip().casefold()
        if not keyword:
            raise ValueError("검색어를 비워 둘 수 없습니다.")
        return [
            book
            for book in self.list_books()
            if keyword
            in f"{book.title} {book.author} {book.isbn}".casefold()
        ]

    def get_book(self, isbn: str) -> Book:
        isbn = isbn.strip()
        book = self.books.get(isbn)
        if book is None:
            raise ValueError(f"등록되지 않은 도서입니다: {isbn}")
        return book

    def borrow_book(self, isbn: str) -> Book:
        book = self.get_book(isbn)
        book.borrow()
        self.history.append((timestamp(), "대여", book.isbn))
        return book

    def return_book(self, isbn: str) -> Book:
        book = self.get_book(isbn)
        book.return_book()
        self.history.append((timestamp(), "반납", book.isbn))
        return book

    def record_error(self, action: str, error: Exception) -> None:
        self.error_logs.append((timestamp(), action, str(error)))

    def statistics(self) -> tuple[Counter[str], list[Book]]:
        monthly_loans = Counter(
            occurred_at.strftime("%Y-%m")
            for occurred_at, action, _ in self.history
            if action == "대여"
        )
        ranking = sorted(
            (book for book in self.books.values() if book.borrow_count > 0),
            key=lambda book: (-book.borrow_count, book.title),
        )
        return monthly_loans, ranking


def create_book_from_input() -> Book:
    print("\n도서 유형: 1. 일반 도서  2. 단행본  3. 전자도서")
    book_type = integer_input("유형을 선택하세요: ")
    if book_type not in {1, 2, 3}:
        raise ValueError("도서 유형은 1~3 중에서 선택해 주세요.")

    title = required_input("도서명: ")
    author = required_input("저자: ")
    isbn = required_input("ISBN: ")
    publication_year = integer_input("출판 연도: ", minimum=1)

    if book_type == 1:
        return Book(title, author, isbn, publication_year)
    if book_type == 2:
        genre = required_input("장르: ")
        return Novel(title, author, isbn, publication_year, genre)

    file_size = float_input("파일 크기(MB): ", minimum=0.1)
    file_format = required_input("파일 형식(PDF/EPUB 등): ").upper()
    return Ebook(
        title, author, isbn, publication_year, file_size, file_format
    )


def print_books(books: list[Book]) -> None:
    if not books:
        print("조회된 도서가 없습니다.")
        return
    for index, book in enumerate(books, start=1):
        print(f"{index}. {book.get_details()}")


def show_statistics(library: Library) -> None:
    monthly_loans, ranking = library.statistics()
    print("\n[월별 대여 건수]")
    if monthly_loans:
        for month, count in sorted(monthly_loans.items()):
            print(f"- {month}: {count}건")
    else:
        print("- 대여 이력이 없습니다.")

    print("[최다 대여 도서]")
    if ranking:
        highest = ranking[0].borrow_count
        for book in ranking:
            if book.borrow_count != highest:
                break
            print(f"- {book.title} ({book.isbn}): {highest}회")
    else:
        print("- 대여 이력이 없습니다.")


def show_error_logs(library: Library) -> None:
    print("\n[오류 로그]")
    if not library.error_logs:
        print("기록된 오류가 없습니다.")
        return
    for occurred_at, action, message in library.error_logs:
        print(f"- {format_time(occurred_at)} | {action} | {message}")


def print_menu() -> None:
    print(
        "\n=== 중앙 도서관 관리 시스템 ===\n"
        "1. 도서 등록\n"
        "2. 전체 도서 조회\n"
        "3. 도서 검색\n"
        "4. 대여/반납 처리\n"
        "5. 종료\n"
        "6. 통계 조회\n"
        "7. 오류 로그 조회"
    )


def run(library: Library | None = None) -> None:
    library = library or Library()
    while True:
        print_menu()
        try:
            menu = integer_input("메뉴를 선택하세요: ")

            if menu == 1:
                book = create_book_from_input()
                library.add_book(book)
                print(f"'{book.title}' 도서가 등록되었습니다.")
            elif menu == 2:
                print_books(library.list_books())
            elif menu == 3:
                keyword = required_input("검색어(도서명/저자/ISBN): ")
                print_books(library.search_books(keyword))
            elif menu == 4:
                action = integer_input("1. 대여  2. 반납: ")
                isbn = required_input("ISBN: ")
                if action == 1:
                    book = library.borrow_book(isbn)
                    print(f"'{book.title}' 도서가 대여되었습니다.")
                elif action == 2:
                    book = library.return_book(isbn)
                    print(f"'{book.title}' 도서가 반납되었습니다.")
                else:
                    raise ValueError("대여는 1, 반납은 2를 입력해 주세요.")
            elif menu == 5:
                print("도서관 시스템을 종료합니다.")
                break
            elif menu == 6:
                show_statistics(library)
            elif menu == 7:
                show_error_logs(library)
            else:
                raise ValueError("메뉴 번호는 1~7 중에서 선택해 주세요.")
        except (ValueError, TypeError) as error:
            library.record_error("메뉴 처리", error)
            print(f"입력 오류: {error}")


def main() -> None:
    run()


if __name__ == "__main__":
    main()
