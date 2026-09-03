from models import Book, Ebook, Novel
from utils import integer_input, required_input

class Library:
    """여러 도서를 등록하고 조회하는 클래스."""

    def __init__(self):
        self.books: dict[str, Book] = {}
        self.book_ids: set[str] = set()

    def add_book(self, book: Book) -> None:
        if book.isbn in self.book_ids:
            raise ValueError(
                f"이미 등록된 ISBN입니다: {book.isbn}"
            )

        self.books[book.isbn] = book
        self.book_ids.add(book.isbn)

    def list_books(self) -> list[Book]:
        return sorted(
            self.books.values(),
            key=lambda book: (
                book.title,
                book.isbn,
            ),
        )

    def search_books(self, keyword: str) -> list[Book]:
        keyword = keyword.strip().casefold()

        if not keyword:
            raise ValueError(
                "검색어를 비워 둘 수 없습니다."
            )

        result = []

        for book in self.books.values():
            book_information = (
                f"{book.title} "
                f"{book.author} "
                f"{book.isbn}"
            ).casefold()

            if keyword in book_information:
                result.append(book)

        return sorted(
            result,
            key=lambda book: (
                book.title,
                book.isbn,
            ),
        )
    def get_book(self, isbn: str) -> Book:
        isbn = isbn.strip()
        book = self.books.get(isbn)

        if book is None:
            raise ValueError(
                f"등록되지 않은 도서입니다: {isbn}"
            )

        return book

    def borrow_book(self, isbn: str) -> Book:
        book = self.get_book(isbn)
        book.borrow()

        return book

    def return_book(self, isbn: str) -> Book:
        book = self.get_book(isbn)
        book.return_book()

        return book

def create_book_from_input() -> Book:
    print("\n도서 유형")
    print("1. 일반 도서")
    print("2. 단행본")
    print("3. 전자도서")

    book_type = integer_input(
        "도서 유형을 선택하세요: "
    )

    if book_type not in {1, 2, 3}:
        raise ValueError(
            "도서 유형은 1~3 중에서 선택해 주세요."
        )

    title = required_input("도서명: ")
    author = required_input("저자: ")
    isbn = required_input("ISBN: ")

    publication_year = integer_input(
        "출판 연도: ",
        minimum=1,
    )

    if book_type == 1:
        return Book(
            title,
            author,
            isbn,
            publication_year,
        )

    if book_type == 2:
        return Novel(
            title,
            author,
            isbn,
            publication_year,
        )

    return Ebook(
        title,
        author,
        isbn,
        publication_year,
    )   

def print_books(books: list[Book]) -> None:
    if not books:
        print("조회된 도서가 없습니다.")
        return

    for index, book in enumerate(
        books,
        start=1,
    ):
        print(
            f"{index}. {book.get_details()}"
        )

def print_menu() -> None:
    print("\n=== 중앙 도서관 관리 시스템 ===")
    print("1. 도서 등록")
    print("2. 전체 도서 조회")
    print("3. 도서 검색")
    print("4. 대여/반납 처리")
    print("5. 종료")

def process_lending(
    library: Library,
) -> None:
    print("\n1. 도서 대여")
    print("2. 도서 반납")

    action = integer_input(
        "처리할 작업을 선택하세요: "
    )

    isbn = required_input("ISBN: ")

    if action == 1:
        book = library.borrow_book(isbn)

        print(
            f"'{book.title}' 도서가 "
            "대여되었습니다."
        )

    elif action == 2:
        book = library.return_book(isbn)

        print(
            f"'{book.title}' 도서가 "
            "반납되었습니다."
        )

    else:
        raise ValueError(
            "대여는 1, 반납은 2를 "
            "입력해 주세요."
        )

def run() -> None:
    library = Library()

    while True:
        print_menu()

        try:
            menu = integer_input(
                "메뉴를 선택하세요: "
            )

            if menu == 1:
                book = create_book_from_input()
                library.add_book(book)

                print(
                    f"'{book.title}' 도서가 "
                    "등록되었습니다."
                )

            elif menu == 2:
                print("\n[전체 도서]")
                print_books(
                    library.list_books()
                )

            elif menu == 3:
                keyword = required_input(
                    "검색어(도서명/저자/ISBN): "
                )

                result = library.search_books(
                    keyword
                )

                print("\n[검색 결과]")
                print_books(result)

            elif menu == 4:
                process_lending(library)

            elif menu == 5:
                print(
                    "도서관 시스템을 종료합니다."
                )
                break

            else:
                raise ValueError(
                    "메뉴 번호는 1~5 중에서 "
                    "선택해 주세요."
                )

        except (ValueError, TypeError) as error:
            print(f"입력 오류: {error}")  

def main() -> None:
    run()

if __name__ == "__main__":
    main()