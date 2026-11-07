"""퀴즈 한 문제를 표현하는 Quiz 클래스."""

CHOICE_COUNT = 4  # 모든 퀴즈의 선택지 개수 (정답 번호는 1~4)


class Quiz:
    """문제(question), 선택지(choices), 정답 번호(answer), 힌트(hint)를 가진 퀴즈 한 문제."""

    def __init__(self, question, choices, answer, hint=""):
        # self는 '지금 만들어지는 바로 그 객체'를 가리킨다.
        # self.속성 = 값 형태로 객체마다 자기 데이터를 따로 보관한다.
        self.question = question
        self.choices = list(choices)
        self.answer = answer  # 정답 번호 (1부터 시작)
        self.hint = hint  # 힌트가 없으면 빈 문자열

    def display(self, number):
        """문제 번호, 문제, 선택지를 화면에 출력한다."""
        print(f"[문제 {number}]")
        print(self.question)
        print()
        for index, choice in enumerate(self.choices, start=1):
            print(f"{index}. {choice}")
        print()

    def is_correct(self, choice_number):
        """사용자가 고른 번호가 정답이면 True, 아니면 False를 반환한다."""
        return choice_number == self.answer

    def correct_choice_text(self):
        """정답 선택지의 내용을 반환한다. (정답 번호는 1부터, 리스트 인덱스는 0부터 시작)"""
        return self.choices[self.answer - 1]

    def to_dict(self):
        """JSON 파일로 저장할 수 있도록 딕셔너리로 바꾼다."""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data):
        """state.json에서 읽은 딕셔너리로 Quiz 객체를 만든다.

        cls는 Quiz 클래스 자신을 가리킨다. (cls(...) == Quiz(...))
        데이터 형식이 잘못되었으면 ValueError를 발생시킨다.
        """
        if not isinstance(data, dict):
            raise ValueError("퀴즈 데이터가 딕셔너리 형태가 아닙니다.")
        question = data.get("question")
        choices = data.get("choices")
        answer = data.get("answer")
        hint = data.get("hint", "")  # 힌트 기능 이전에 저장한 파일에는 hint가 없을 수 있다.

        if not isinstance(question, str) or not question.strip():
            raise ValueError("question(문제)이 비어 있거나 문자열이 아닙니다.")
        if not isinstance(choices, list) or len(choices) != CHOICE_COUNT:
            raise ValueError(f"choices(선택지)는 {CHOICE_COUNT}개짜리 목록이어야 합니다.")
        for choice in choices:
            if not isinstance(choice, str) or not choice.strip():
                raise ValueError("choices에 비어 있거나 문자열이 아닌 값이 있습니다.")
        # bool은 int의 하위 타입이라(True == 1) 따로 걸러 낸다.
        if isinstance(answer, bool) or not isinstance(answer, int) or not 1 <= answer <= CHOICE_COUNT:
            raise ValueError(f"answer(정답)는 1-{CHOICE_COUNT} 사이의 정수여야 합니다.")
        if not isinstance(hint, str):
            raise ValueError("hint(힌트)는 문자열이어야 합니다.")
        return cls(question, choices, answer, hint)
