from .base_book import Book

class Novel(Book):

    @property
    def book_type(self) -> str:
        return "단행본"

class Ebook(Book):

    @property
    def book_type(self) -> str:
        return "전자도서"