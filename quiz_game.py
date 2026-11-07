"""퀴즈 게임 전체 흐름을 관리하는 QuizGame 클래스."""

from default_quizzes import get_default_quizzes
from input_utils import read_int

LINE = "=" * 40
THIN_LINE = "-" * 40
MENU_ITEMS = ["퀴즈 풀기", "퀴즈 추가", "퀴즈 목록", "점수 확인", "종료"]
EXIT_MENU = len(MENU_ITEMS)  # 마지막 메뉴가 '종료'


class QuizGame:
    """메뉴를 보여 주고, 사용자가 고른 기능을 실행하는 게임 관리 클래스."""

    def __init__(self):
        self.quizzes = get_default_quizzes()  # Quiz 객체 목록

    def run(self):
        """프로그램의 메인 루프. '종료'를 고를 때까지 메뉴를 반복한다."""
        try:
            while True:
                self.show_menu()
                choice = read_int("선택: ", 1, EXIT_MENU)
                print()
                if choice == EXIT_MENU:
                    break
                self.handle_menu(choice)
                print()
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C 또는 입력 스트림 종료(Ctrl+D / Ctrl+Z) → 오류 메시지 대신 안전하게 종료
            print("\n\n⚠️ 입력이 중단되어 게임을 종료합니다.")
        print("👋 게임을 종료합니다. 다음에 또 만나요!")

    def show_menu(self):
        """메인 메뉴를 출력한다."""
        print(LINE)
        print("        🎯 나만의 퀴즈 게임 🎯")
        print(LINE)
        for number, title in enumerate(MENU_ITEMS, start=1):
            print(f"{number}. {title}")
        print(LINE)

    def handle_menu(self, choice):
        """메뉴 번호에 맞는 기능을 실행한다."""
        if choice == 1:
            self.play_quiz()
        elif choice == 2:
            self.add_quiz()
        elif choice == 3:
            self.list_quizzes()
        elif choice == 4:
            self.show_score()

    def play_quiz(self):
        """저장된 퀴즈를 순서대로 출제하고, 모두 풀면 결과를 보여 준다."""
        if not self.quizzes:
            print("📭 등록된 퀴즈가 없습니다. 먼저 '2. 퀴즈 추가'에서 퀴즈를 등록해 주세요.")
            return

        total = len(self.quizzes)
        correct_count = 0
        print(f"📝 퀴즈를 시작합니다! (총 {total}문제)")
        for number, quiz in enumerate(self.quizzes, start=1):
            print()
            print(THIN_LINE)
            quiz.display(number)
            max_choice = len(quiz.choices)
            choice = read_int(f"정답 입력 (1-{max_choice}): ", 1, max_choice)
            if quiz.is_correct(choice):
                correct_count += 1
                print("✅ 정답입니다!")
            else:
                print(f"❌ 오답입니다. 정답은 {quiz.answer}번 ({quiz.correct_choice_text()})입니다.")

        score = round(correct_count / total * 100)
        print()
        print(LINE)
        print(f"🏆 결과: {total}문제 중 {correct_count}문제 정답! ({score}점)")
        print(LINE)

    def add_quiz(self):
        print("🚧 퀴즈 추가는 준비 중인 기능입니다.")

    def list_quizzes(self):
        print("🚧 퀴즈 목록은 준비 중인 기능입니다.")

    def show_score(self):
        print("🚧 점수 확인은 준비 중인 기능입니다.")
