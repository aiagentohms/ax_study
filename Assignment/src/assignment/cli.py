from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .domain import LibraryError
from .service import LibraryService
from .storage import JsonRepository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="assignment", description="도서관 도서 대출·반납 시스템"
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("library_data.json"),
        help="데이터 파일 경로 (기본값: library_data.json)",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    add_book = commands.add_parser("add-book", help="도서 등록")
    add_book.add_argument("isbn")
    add_book.add_argument("title")
    add_book.add_argument("author")
    add_book.add_argument("--copies", type=int, default=1)

    add_member = commands.add_parser("add-member", help="회원 등록")
    add_member.add_argument("member_id")
    add_member.add_argument("name")
    add_member.add_argument("--max-loans", type=int, default=5)

    books = commands.add_parser("books", help="도서 검색 및 대출 가능 수량 조회")
    books.add_argument("--query", default="")

    borrow = commands.add_parser("borrow", help="도서 대출")
    borrow.add_argument("isbn")
    borrow.add_argument("member_id")
    borrow.add_argument("--days", type=int, default=14)

    return_book = commands.add_parser("return", help="도서 반납")
    return_book.add_argument("isbn")
    return_book.add_argument("member_id")

    loans = commands.add_parser("loans", help="대출 기록 조회")
    loans.add_argument("--all", action="store_true", help="반납 완료 기록도 표시")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        service = LibraryService(JsonRepository(args.data))

        if args.command == "add-book":
            book = service.add_book(args.isbn, args.title, args.author, args.copies)
            print(f"도서 등록 완료: {book.title} ({book.isbn}), {book.total_copies}권")
        elif args.command == "add-member":
            member = service.add_member(args.member_id, args.name, args.max_loans)
            print(f"회원 등록 완료: {member.name} ({member.member_id})")
        elif args.command == "books":
            books = service.search_books(args.query)
            if not books:
                print("검색 결과가 없습니다.")
            for item in books:
                print(
                    f"{item.book.isbn} | {item.book.title} | {item.book.author} | "
                    f"대출 가능 {item.available_copies}/{item.book.total_copies}"
                )
        elif args.command == "borrow":
            loan = service.borrow_book(args.isbn, args.member_id, loan_days=args.days)
            print(f"대출 완료: 반납 예정일 {loan.due_on.isoformat()}")
        elif args.command == "return":
            receipt = service.return_book(args.isbn, args.member_id)
            if receipt.overdue_days:
                print(f"반납 완료: {receipt.overdue_days}일 연체")
            else:
                print("반납 완료: 연체 없음")
        elif args.command == "loans":
            loans = service.list_loans(active_only=not args.all)
            if not loans:
                print("대출 기록이 없습니다.")
            for loan in loans:
                status = (
                    f"반납 {loan.returned_on.isoformat()}"
                    if loan.returned_on
                    else f"대출 중 / 예정일 {loan.due_on.isoformat()}"
                )
                print(f"{loan.loan_id} | {loan.isbn} | {loan.member_id} | {status}")
        return 0
    except (LibraryError, ValueError, OSError, json.JSONDecodeError) as error:
        print(f"오류: {error}", file=sys.stderr)
        return 1
