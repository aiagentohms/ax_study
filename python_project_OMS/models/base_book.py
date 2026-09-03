class Book:
    """도서 공통 사용 기본 클래스"""
    def __init__(
            self,
            title: str,
            author: str,
            isbn: str,
            publication_year: int,
    ):
        title = title.strip()
        author = author.strip()
        isbn = isbn.strip()

        if not title or not author or not isbn:
            raise ValueError(
                "도서명, 저자, ISBN은 비워 둘 수 없습니다."
            )
        if publication_year < 1900:
            raise ValueError(
                "출판 연도는 1900년도 이상으로 적어주세요"
            )

        self.__title = title
        self.__author = author
        self.__isbn = isbn
        self.__publication_year = publication_year
        self.__is_borrowed = False

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

    def borrow(self) -> None:
        if self.__is_borrowed:
            raise ValueError(
                "이미 대여 중인 도서입니다."
            )

        self.__is_borrowed = True

    def return_book(self) -> None:
        if not self.__is_borrowed:
            raise ValueError(
                "현재 대여 중인 도서가 아닙니다."
            )

        self.__is_borrowed = False

    @property
    def book_type(self) -> str:
        return "일반 도서"

    def get_details(self) -> str:
        if self.is_borrowed:
            status = "대여 중"
        else:
            status = "대여 가능"

        return (
            f"[{self.book_type}]"
            f"{self.title} / "
            f"{self.author} / "
            f"ISBN: {self.isbn} / "
            f"{self.publication_year}년 / "
            f"{status}"
        )