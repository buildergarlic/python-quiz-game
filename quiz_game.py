"""퀴즈 게임 전체 흐름을 관리하는 QuizGame 클래스.

QuizGame의 역할
  - 메뉴 표시와 선택한 기능 실행
  - 퀴즈 풀기 / 추가 / 목록 / 점수 확인 / 삭제 / 게임 기록
  - 데이터 저장·불러오기 요청 (실제 파일 처리는 StateStorage가 담당)
"""

import random
from datetime import datetime

from default_quizzes import get_default_quizzes
from input_utils import parse_int, read_int, read_text, read_yes_no
from quiz import CHOICE_COUNT, Quiz

LINE = "=" * 40
THIN_LINE = "-" * 40
HINT_CREDIT = 0.5  # 힌트를 보고 맞힌 문제는 배점의 절반만 인정
HISTORY_DISPLAY_LIMIT = 10  # 게임 기록 화면에 보여 줄 최근 기록 수
MENU_ITEMS = ["퀴즈 풀기", "퀴즈 추가", "퀴즈 목록", "점수 확인", "퀴즈 삭제", "게임 기록", "종료"]
EXIT_MENU = len(MENU_ITEMS)  # 마지막 메뉴가 '종료'


class QuizGame:
    """퀴즈 목록, 최고 점수, 게임 기록을 가지고 메뉴에 따라 각 기능을 실행하는 클래스."""

    def __init__(self, storage):
        self.storage = storage  # state.json 저장/불러오기 담당 (StateStorage 객체)
        self.quizzes = []  # Quiz 객체 목록
        self.best_score = None  # 최고 점수 (아직 한 번도 풀지 않았으면 None)
        self.history = []  # 게임 기록 목록 (한 판 = 딕셔너리 하나)
        self.can_save = True  # 기존 파일을 보호해야 할 때 False (저장하지 않음)

    # ------------------------------------------------------------
    # 실행 / 메뉴
    # ------------------------------------------------------------
    def run(self):
        """프로그램의 메인 루프. '종료'를 고를 때까지 메뉴를 반복한다."""
        message = self.load_state()
        try:
            while True:
                self.show_menu(message)
                message = None  # 불러오기 안내는 첫 화면에서만 보여 준다.
                choice = read_int("선택: ", 1, EXIT_MENU)
                print()
                if choice == EXIT_MENU:
                    break
                self.handle_menu(choice)
                print()
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C 또는 입력 스트림 종료(Ctrl+D / Ctrl+Z) → 오류 메시지 대신 저장 후 종료
            print("\n\n⚠️ 입력이 중단되었습니다. 데이터를 저장하고 안전하게 종료합니다.")
        self.save_state()
        print("👋 게임을 종료합니다. 다음에 또 만나요!")

    def show_menu(self, message=None):
        """메인 메뉴를 출력한다. message가 있으면 제목 아래에 함께 보여 준다."""
        print(LINE)
        print("        🎯 나만의 퀴즈 게임 🎯")
        print(LINE)
        if message:
            print(message)
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
        elif choice == 5:
            self.delete_quiz()
        elif choice == 6:
            self.show_history()

    # ------------------------------------------------------------
    # 1. 퀴즈 풀기
    # ------------------------------------------------------------
    def play_quiz(self):
        """풀 문제 수를 고르게 한 뒤 퀴즈를 무작위 순서로 출제하고, 모두 풀면 결과를 보여 준다."""
        if not self.quizzes:
            print("📭 등록된 퀴즈가 없습니다. 먼저 '2. 퀴즈 추가'에서 퀴즈를 등록해 주세요.")
            return

        total = len(self.quizzes)
        count = read_int(f"몇 문제를 풀까요? (1-{total}): ", 1, total)
        # 원본 목록의 순서는 그대로 두고, 무작위로 count개를 뽑아 새 리스트를 만든다.
        selected = random.sample(self.quizzes, count)

        print(f"\n📝 퀴즈를 시작합니다! (총 {count}문제)")
        print("💡 정답 대신 h를 입력하면 힌트를 볼 수 있어요. (힌트를 보고 맞히면 절반 점수)")
        correct_count = 0
        hints_used = 0
        earned_points = 0.0  # 맞힌 문제당 1점, 힌트를 보고 맞힌 문제는 HINT_CREDIT점
        for number, quiz in enumerate(selected, start=1):
            is_correct, used_hint = self._play_one(number, quiz)
            if used_hint:
                hints_used += 1
            if is_correct:
                correct_count += 1
                if used_hint:
                    earned_points += HINT_CREDIT
                else:
                    earned_points += 1

        score = round(earned_points / count * 100)
        self._finish_game(count, correct_count, hints_used, score)

    def _play_one(self, number, quiz):
        """퀴즈 한 문제를 출제한다. 반환값: (맞혔는지 여부, 힌트를 봤는지 여부)"""
        print()
        print(THIN_LINE)
        quiz.display(number)
        choice, used_hint = self._ask_answer(quiz)
        if quiz.is_correct(choice):
            print("✅ 정답입니다!")
            return True, used_hint
        print(f"❌ 오답입니다. 정답은 {quiz.answer}번 ({quiz.correct_choice_text()})입니다.")
        return False, used_hint

    def _ask_answer(self, quiz):
        """정답 번호를 입력받는다. h를 입력하면 힌트를 보여 준다.

        반환값: (선택한 번호, 힌트를 봤는지 여부)
        """
        max_choice = len(quiz.choices)
        used_hint = False
        while True:
            raw = input(f"정답 입력 (1-{max_choice}, 힌트 h): ")
            # 한글 자판 상태에서 h 키를 누르면 'ㅗ'가 입력되므로 함께 허용한다.
            if raw.strip().lower() in ("h", "ㅗ"):
                if quiz.hint:
                    print(f"💡 힌트: {quiz.hint}")
                    used_hint = True
                else:
                    print("💡 이 문제에는 힌트가 없습니다. (점수 차감 없음)")
                continue
            number, error = parse_int(raw, 1, max_choice)
            if error is None:
                return number, used_hint
            print(error)

    def _finish_game(self, total, correct_count, hints_used, score):
        """게임 결과를 출력하고, 최고 점수와 게임 기록을 갱신한 뒤 저장한다."""
        is_new_best = self._update_best_score(score)
        print()
        print(LINE)
        print(f"🏆 결과: {total}문제 중 {correct_count}문제 정답! ({score}점)")
        if hints_used > 0:
            print(f"💡 힌트 사용: {hints_used}회 (힌트를 보고 맞힌 문제는 절반 점수)")
        if is_new_best:
            print("🎉 새로운 최고 점수입니다!")
        else:
            print(f"📌 현재 최고 점수는 {self.best_score}점입니다. 다음에 다시 도전해 보세요!")
        print(LINE)

        self.history.append({
            "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": total,
            "correct": correct_count,
            "hints_used": hints_used,
            "score": score,
        })
        self.save_state()

    def _update_best_score(self, score):
        """점수가 최고 점수보다 높으면 갱신하고 True를, 아니면 False를 반환한다."""
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            return True
        return False

    # ------------------------------------------------------------
    # 2. 퀴즈 추가
    # ------------------------------------------------------------
    def add_quiz(self):
        """문제, 선택지 4개, 정답 번호, 힌트(선택)를 입력받아 새 퀴즈를 등록한다."""
        print("📌 새로운 퀴즈를 추가합니다.\n")
        question = read_text("문제를 입력하세요: ")
        choices = []
        for number in range(1, CHOICE_COUNT + 1):
            choices.append(self._read_new_choice(number, choices))
        answer = read_int(f"정답 번호 (1-{CHOICE_COUNT}): ", 1, CHOICE_COUNT)
        hint = input("힌트 (없으면 그냥 Enter): ").strip()

        self.quizzes.append(Quiz(question, choices, answer, hint))
        print(f"\n✅ 퀴즈가 추가되었습니다! (총 {len(self.quizzes)}개)")
        self.save_state()

    def _read_new_choice(self, number, existing_choices):
        """이미 입력한 선택지와 겹치지 않는 선택지를 입력받는다."""
        while True:
            choice = read_text(f"선택지 {number}: ")
            if choice not in existing_choices:
                return choice
            print("⚠️ 이미 입력한 선택지입니다. 다른 내용을 입력하세요.")

    # ------------------------------------------------------------
    # 3. 퀴즈 목록
    # ------------------------------------------------------------
    def list_quizzes(self):
        """등록된 퀴즈의 문제를 번호와 함께 보여 준다."""
        if not self.quizzes:
            print("📭 등록된 퀴즈가 없습니다. '2. 퀴즈 추가'에서 퀴즈를 등록해 주세요.")
            return

        print(f"📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개, 💡 = 힌트 있음)\n")
        print(THIN_LINE)
        for number, quiz in enumerate(self.quizzes, start=1):
            hint_mark = " 💡" if quiz.hint else ""
            print(f"[{number}] {quiz.question}{hint_mark}")
        print(THIN_LINE)

    # ------------------------------------------------------------
    # 4. 점수 확인
    # ------------------------------------------------------------
    def show_score(self):
        """최고 점수와, 그 점수를 기록한 게임의 정답 수를 보여 준다."""
        if self.best_score is None:
            print("📭 아직 퀴즈를 풀지 않았습니다. '1. 퀴즈 풀기'로 도전해 보세요!")
            return

        record = self._find_best_record()
        if record is None:
            print(f"🏆 최고 점수: {self.best_score}점")
        else:
            print(
                f"🏆 최고 점수: {self.best_score}점 "
                f"({record['total']}문제 중 {record['correct']}문제 정답, {record['played_at']})"
            )
        print(f"🎮 기록된 게임 수: {len(self.history)}회 ('6. 게임 기록'에서 확인)")

    def _find_best_record(self):
        """게임 기록 중 최고 점수를 처음 달성한 기록을 찾는다. 없으면 None을 반환한다."""
        for record in self.history:
            if record["score"] == self.best_score:
                return record
        return None

    def _best_score_text(self):
        """최고 점수를 화면 표시용 문자열로 바꾼다. (예: '80점', '없음')"""
        if self.best_score is None:
            return "없음"
        return f"{self.best_score}점"

    # ------------------------------------------------------------
    # 5. 퀴즈 삭제
    # ------------------------------------------------------------
    def delete_quiz(self):
        """목록에서 번호를 골라 퀴즈를 삭제하고 파일에 반영한다."""
        if not self.quizzes:
            print("📭 삭제할 퀴즈가 없습니다.")
            return

        self.list_quizzes()
        total = len(self.quizzes)
        number = read_int(f"삭제할 퀴즈 번호 (1-{total}, 취소는 0): ", 0, total)
        if number == 0:
            print("↩️ 삭제를 취소했습니다.")
            return

        quiz = self.quizzes[number - 1]  # 화면 번호는 1부터, 리스트 인덱스는 0부터
        if not read_yes_no(f"'{quiz.question}' 퀴즈를 삭제할까요? (y/n): "):
            print("↩️ 삭제를 취소했습니다.")
            return

        self.quizzes.pop(number - 1)
        print(f"🗑️ 퀴즈를 삭제했습니다. (남은 퀴즈 {len(self.quizzes)}개)")
        self.save_state()

    # ------------------------------------------------------------
    # 6. 게임 기록
    # ------------------------------------------------------------
    def show_history(self):
        """최근 게임 기록을 최신순으로 보여 준다."""
        if not self.history:
            print("📭 아직 게임 기록이 없습니다. '1. 퀴즈 풀기'로 첫 기록을 남겨 보세요!")
            return

        recent = self.history[-HISTORY_DISPLAY_LIMIT:]  # 슬라이싱: 마지막 최대 10개
        print(f"📜 게임 기록 (최근 {len(recent)}회 / 전체 {len(self.history)}회)\n")
        print(THIN_LINE)
        for record in reversed(recent):  # 최신 기록이 맨 위에 오도록 뒤집어서 출력
            print(
                f"{record['played_at']} | {record['total']}문제 중 {record['correct']}문제 정답"
                f" | 힌트 {record['hints_used']}회 | {record['score']}점"
            )
        print(THIN_LINE)

    # ------------------------------------------------------------
    # 파일 저장 / 불러오기
    # ------------------------------------------------------------
    def load_state(self):
        """state.json에서 데이터를 불러오고, 첫 화면에 보여 줄 안내 문구를 반환한다."""
        status, data = self.storage.load()
        if status == "loaded":
            self.quizzes = data["quizzes"]
            self.best_score = data["best_score"]
            self.history = data["history"]
            return (
                "📂 저장된 데이터를 불러왔습니다. "
                f"(퀴즈 {len(self.quizzes)}개, 최고점수 {self._best_score_text()})"
            )

        # 파일이 없거나 쓸 수 없는 상태면 기본 퀴즈로 시작한다.
        self.quizzes = get_default_quizzes()
        self.best_score = None
        self.history = []
        if status == "missing":
            self.save_state()
            return f"📂 저장된 데이터가 없어 기본 퀴즈 {len(self.quizzes)}개로 시작합니다."
        if status == "corrupted" and self.storage.backup_corrupted_file():
            self.save_state()
            return (
                "⚠️ state.json이 손상되어 기본 퀴즈 데이터로 복구했습니다.\n"
                f"   (손상된 파일은 {self.storage.backup_path.name}에 백업해 두었습니다.)"
            )
        # 파일을 읽을 수 없거나 백업에 실패한 경우: 기존 파일을 덮어쓰지 않도록 저장을 끈다.
        self.can_save = False
        return (
            "⚠️ state.json을 불러오지 못해 기본 퀴즈로 시작합니다.\n"
            "   (기존 파일을 보호하기 위해 이번 실행에서는 저장하지 않습니다.)"
        )

    def save_state(self):
        """현재 퀴즈 목록, 최고 점수, 게임 기록을 state.json에 저장한다. 성공하면 True를 반환한다."""
        if not self.can_save:
            return False
        try:
            self.storage.save(self.quizzes, self.best_score, self.history)
        except OSError as error:
            print(f"⚠️ 데이터를 파일에 저장하지 못했습니다: {error}")
            return False
        return True
