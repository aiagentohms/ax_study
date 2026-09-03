from .base_book import Book


class Novel(Book):
    """장르 정보를 추가로 가지는 단행본."""

    def __init__(
        self,
        title: str,
        author: str,
        isbn: str,
        publication_year: int,
        genre: str,
    ):
        super().__init__(title, author, isbn, publication_year)
        genre = genre.strip()
        if not genre:
            raise ValueError("장르는 비워 둘 수 없습니다.")
        self.__genre = genre

    @property
    def genre(self) -> str:
        return self.__genre

    @property
    def book_type(self) -> str:
        return "단행본"

    def get_details(self) -> str:
        return f"{super().get_details()} / 장르: {self.genre}"


class Ebook(Book):
    """파일 크기와 형식을 추가로 가지는 전자도서."""

    def __init__(
        self,
        title: str,
        author: str,
        isbn: str,
        publication_year: int,
        file_size_mb: float,
        file_format: str = "PDF",
    ):
        super().__init__(title, author, isbn, publication_year)
        file_format = file_format.strip().upper()
        if file_size_mb <= 0:
            raise ValueError("파일 크기는 0보다 커야 합니다.")
        if not file_format:
            raise ValueError("파일 형식은 비워 둘 수 없습니다.")
        self.__file_size_mb = file_size_mb
        self.__file_format = file_format

    @property
    def file_size_mb(self) -> float:
        return self.__file_size_mb

    @property
    def file_format(self) -> str:
        return self.__file_format

    @property
    def book_type(self) -> str:
        return "전자도서"

    def get_details(self) -> str:
        return (
            f"{super().get_details()} / 파일: "
            f"{self.file_size_mb:g}MB {self.file_format}"
        )
