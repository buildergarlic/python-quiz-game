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


def read_int(prompt, min_value, max_value):
    """min_value 이상 max_value 이하의 정수를 입력받을 때까지 반복해서 묻는다.

    - 입력 앞뒤 공백은 제거한다. (" 1 " -> 1)
    - 빈 입력, 숫자가 아닌 입력, 범위 밖 숫자는 안내 메시지를 보여 주고 다시 묻는다.
    """
    guide = f"{min_value}-{max_value} 사이의 숫자를 입력하세요."
    while True:
        raw = input(prompt).strip()
        if raw == "":
            print(f"⚠️ 입력이 비어 있습니다. {guide}")
            continue
        try:
            number = int(raw)
        except ValueError:
            print(f"⚠️ 잘못된 입력입니다. {guide}")
            continue
        if min_value <= number <= max_value:
            return number
        print(f"⚠️ 잘못된 입력입니다. {guide}")
