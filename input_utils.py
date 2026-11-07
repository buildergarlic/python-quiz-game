"""사용자 입력을 안전하게 받기 위한 공통 함수 모음.

input()에서 발생하는 KeyboardInterrupt(Ctrl+C)와 EOFError(입력 스트림 종료)는
여기서 잡지 않고 호출한 쪽으로 그대로 올려 보낸다.
QuizGame.run()이 한곳에서 받아 '저장 후 안전 종료'를 처리한다.
"""


def read_text(prompt):
    """비어 있지 않은 문자열을 입력받아 앞뒤 공백을 제거해 반환한다."""
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("⚠️ 입력이 비어 있습니다. 내용을 입력하세요.")


def parse_int(raw, min_value, max_value):
    """문자열을 min_value 이상 max_value 이하의 정수로 바꾼다.

    - 입력 앞뒤 공백은 제거한다. (" 1 " -> 1)
    반환값: 성공하면 (정수, None), 실패하면 (None, 안내 메시지)
    """
    guide = f"{min_value}-{max_value} 사이의 숫자를 입력하세요."
    text = raw.strip()
    if text == "":
        return None, f"⚠️ 입력이 비어 있습니다. {guide}"
    try:
        number = int(text)
    except ValueError:
        return None, f"⚠️ 잘못된 입력입니다. {guide}"
    if not min_value <= number <= max_value:
        return None, f"⚠️ 잘못된 입력입니다. {guide}"
    return number, None


def read_int(prompt, min_value, max_value):
    """min_value 이상 max_value 이하의 정수를 입력받을 때까지 반복해서 묻는다.

    빈 입력, 숫자가 아닌 입력, 범위 밖 숫자는 안내 메시지를 보여 주고 다시 묻는다.
    """
    while True:
        number, error = parse_int(input(prompt), min_value, max_value)
        if error is None:
            return number
        print(error)
