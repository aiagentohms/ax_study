# Python 기초 과제 - 도서 관리 시스템

과제 발제안의 필수 구조와 채점 기준에 맞춘 대화형 콘솔 프로그램입니다.
`input()`과 `while` 반복문으로 메뉴를 운영하며 객체지향, 자료구조, 예외
처리와 모듈화를 한 프로젝트에서 확인할 수 있습니다.

## 제공 기능

- 일반 도서, 단행본, 전자도서 등록
- ISBN 중복·공백·숫자 입력 검증
- 전체 도서 조회와 제목·저자·ISBN 검색
- 대여 가능 여부 확인 및 대여·반납 상태 전환
- 튜플 기반 대여/반납 이력과 월별 통계
- 최다 대여 도서 및 시간 정보가 포함된 오류 로그

## 실행

프로젝트 폴더에서 다음 명령으로 실행합니다.

```powershell
uv run python main.py
```

## 테스트

외부 테스트 패키지 없이 표준 라이브러리만 사용합니다.

```powershell
uv run python -m unittest discover -s tests -v
```

## 과제 구조

- `models/base_book.py`: 캡슐화된 상위 도서 클래스
- `models/specialized_books.py`: `Novel`, `Ebook` 하위 클래스
- `utils/helpers.py`: 공통 입력 검증과 시간 포맷
- `main.py`: 도서 자료구조, 대여/반납 로직, 대화형 메뉴
- `tests/`: 핵심 업무 규칙 회귀 테스트

## 제출

프로젝트 전체 폴더를 `python_final_project_[수강생이름].zip` 이름으로 압축해
제출합니다. `.py`, `pyproject.toml`, `uv.lock` 파일을 반드시 포함합니다.
