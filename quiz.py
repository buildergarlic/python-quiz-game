"""퀴즈 한 문제를 표현하는 Quiz 클래스."""

CHOICE_COUNT = 4  # 모든 퀴즈의 선택지 개수 (정답 번호는 1~4)


class Quiz:
    """문제(question), 선택지(choices), 정답 번호(answer)를 가진 퀴즈 한 문제."""

    def __init__(self, question, choices, answer):
        # self는 '지금 만들어지는 바로 그 객체'를 가리킨다.
        # self.속성 = 값 형태로 객체마다 자기 데이터를 따로 보관한다.
        self.question = question
        self.choices = list(choices)
        self.answer = answer  # 정답 번호 (1부터 시작)

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
