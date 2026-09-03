"""이전 실습 노트북을 위한 호환 모듈.

새 코드에서는 과제 명세와 같은 ``specialized_books``를 사용한다.
"""

from .specialized_books import Ebook, Novel

__all__ = ["Ebook", "Novel"]
