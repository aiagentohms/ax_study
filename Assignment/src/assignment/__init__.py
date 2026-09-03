"""이전 구현의 패키지 진입점."""


def main() -> int:
    from .cli import main as cli_main

    return cli_main()
