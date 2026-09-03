from datetime import datetime


def required_input(prompt: str) -> str:
    """공백 입력을 거부하고 앞뒤 공백을 제거한다."""
    value = input(prompt).strip()
    if not value:
        raise ValueError("값을 비워 둘 수 없습니다.")
    return value


def integer_input(prompt: str, *, minimum: int | None = None) -> int:
    """정수 입력을 검증한다. 변환 실패는 호출자가 한 곳에서 처리한다."""
    value = int(required_input(prompt))
    if minimum is not None and value < minimum:
        raise ValueError(f"{minimum} 이상의 숫자를 입력해 주세요.")
    return value


def float_input(prompt: str, *, minimum: float | None = None) -> float:
    value = float(required_input(prompt))
    if minimum is not None and value < minimum:
        raise ValueError(f"{minimum:g} 이상의 숫자를 입력해 주세요.")
    return value


def timestamp() -> datetime:
    return datetime.now()


def format_time(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S")
