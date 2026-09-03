def required_input(prompt: str) -> str:
    """공백 입력 X 문자열 입력 함수"""

    value = input(prompt).strip() #문자열 받고 앞뒤 공백 제거, 기입안하면 에러

    if not value:
        raise ValueError(
            "빈값은 불가능합니다"
        )    

    return value

def integer_input(
    prompt: str,
    minimum: int | None = None,
) -> int:
    """정수와 최소값을 검사하는 입력 함수."""

    value = int(required_input(prompt))

    if minimum is not None and value < minimum:
        raise ValueError(
            f"{minimum} 이상의 숫자를 입력하세요."
        )

    return value