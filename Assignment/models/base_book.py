class Book:
    """모든 도서 유형이 공통으로 사용하는 상위 클래스."""

    def __init__(self, title: str, author: str, isbn: str, publication_year: int):
        title = title.strip()
        author = author.strip()
        isbn = isbn.strip()
        if not title or not author or not isbn:
            raise ValueError("도서명, 저자, ISBN은 비워 둘 수 없습니다.")
        if publication_year < 1:
            raise ValueError("출판 연도는 1 이상이어야 합니다.")
        # 직접 수정을 막고 property를 통해서만 읽도록 캡슐화한다.
        self.__title = title
        self.__author = author
        self.__isbn = isbn
        self.__publication_year = publication_year
        self.__is_borrowed = False
        self.__borrow_count = 0

    @property
    def title(self) -> str:
        return self.__title

    @property
    def author(self) -> str:
        return self.__author

    @property
    def isbn(self) -> str:
        return self.__isbn

    @property
    def publication_year(self) -> int:
        return self.__publication_year

    @property
    def is_borrowed(self) -> bool:
        return self.__is_borrowed

    @property
    def borrow_count(self) -> int:
        return self.__borrow_count

    @property
    def book_type(self) -> str:
        return "일반 도서"

    def borrow(self) -> None:
        if self.__is_borrowed:
            raise ValueError("이미 대여 중인 도서입니다.")
        self.__is_borrowed = True
        self.__borrow_count += 1

    def return_book(self) -> None:
        if not self.__is_borrowed:
            raise ValueError("현재 대여 중인 도서가 아닙니다.")
        self.__is_borrowed = False

    def get_details(self) -> str:
        status = "대여 중" if self.is_borrowed else "대여 가능"
        return (
            f"[{self.book_type}] {self.title} / {self.author} / "
            f"ISBN: {self.isbn} / {self.publication_year}년 / {status}"
        )
