"""퀴즈 풀기의 점수 계산·힌트 반영·최고 점수 갱신·기록 저장 테스트 (QuizGame.play_quiz)."""

import unittest
from unittest import mock

from helpers import FakeStorage, typed

from quiz import Quiz
from quiz_game import QuizGame


def make_game():
    """정답이 1, 2, 3번인 퀴즈 3개(세 번째는 힌트 없음)를 가진 게임."""
    game = QuizGame(FakeStorage())
    game.quizzes = [
        Quiz("문제 A", ["a", "b", "c", "d"], 1, "A 힌트"),
        Quiz("문제 B", ["a", "b", "c", "d"], 2, "B 힌트"),
        Quiz("문제 C", ["a", "b", "c", "d"], 3, ""),
    ]
    return game


def play(game, *answers):
    """무작위 대신 목록 순서대로 출제하게 하고, answers를 입력해 한 판을 푼다."""
    with mock.patch("quiz_game.random.sample", lambda items, count: list(items)[:count]):
        with typed(*answers) as output:
            game.play_quiz()
    return output.getvalue()


class ScoringTest(unittest.TestCase):
    def test_all_correct_is_100(self):
        game = make_game()
        output = play(game, "3", "1", "2", "3")
        self.assertIn("3문제 중 3문제 정답! (100점)", output)
        self.assertEqual(game.best_score, 100)

    def test_readme_example_is_50(self):
        # README 예시: 그냥 맞힘 1 + 힌트 보고 맞힘 0.5 + 틀림 0 → 1.5 / 3 × 100 = 50점
        game = make_game()
        output = play(game, "3", "1", "h", "2", "4")
        self.assertIn("3문제 중 2문제 정답! (50점)", output)
        self.assertIn("힌트 사용: 1회", output)
        self.assertEqual(game.history[-1]["score"], 50)
        self.assertEqual(game.history[-1]["hints_used"], 1)

    def test_hint_then_wrong_is_zero(self):
        game = make_game()
        play(game, "1", "h", "4")
        self.assertEqual(game.history[-1]["score"], 0)
        self.assertEqual(game.history[-1]["correct"], 0)

    def test_korean_keyboard_hint_key(self):
        game = make_game()
        output = play(game, "1", "ㅗ", "1")  # 한글 자판에서 h 키 = 'ㅗ'
        self.assertIn("💡 힌트: A 힌트", output)
        self.assertEqual(game.history[-1]["score"], 50)

    def test_no_penalty_when_quiz_has_no_hint(self):
        game = make_game()
        game.quizzes = [game.quizzes[2]]  # 힌트 없는 문제
        output = play(game, "1", "h", "3")
        self.assertIn("이 문제에는 힌트가 없습니다", output)
        self.assertEqual(game.history[-1]["score"], 100)
        self.assertEqual(game.history[-1]["hints_used"], 0)

    def test_score_is_rounded(self):
        game = make_game()
        play(game, "3", "1", "1", "1")  # 1 / 3 × 100 = 33.33… → 33
        self.assertEqual(game.history[-1]["score"], 33)

    def test_best_score_only_goes_up(self):
        game = make_game()
        play(game, "2", "1", "2")  # 100점
        output = play(game, "2", "1", "1")  # 50점
        self.assertEqual(game.best_score, 100)
        self.assertIn("현재 최고 점수는 100점", output)
        output = play(game, "2", "1", "2")  # 같은 100점은 '새 최고 점수'가 아니다.
        self.assertNotIn("새로운 최고 점수", output)
        self.assertEqual(len(game.history), 3)

    def test_result_is_saved_after_each_game(self):
        game = make_game()
        play(game, "1", "1")
        self.assertEqual(game.storage.saved[-1], (3, 100, 1))

    def test_invalid_answers_are_asked_again(self):
        game = make_game()
        output = play(game, "0", "4", "1", "", "x", "5", "1")
        self.assertIn("1-3 사이의 숫자", output)  # 문제 수 0, 4 거부
        self.assertEqual(output.count("1-4 사이의 숫자"), 3)  # 정답 '', x, 5 거부
        self.assertEqual(game.history[-1]["score"], 100)

    def test_no_quizzes(self):
        game = QuizGame(FakeStorage())
        output = play(game)
        self.assertIn("등록된 퀴즈가 없습니다", output)
        self.assertEqual(game.history, [])


if __name__ == "__main__":
    unittest.main()
