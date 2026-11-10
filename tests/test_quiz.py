"""Quiz 클래스와 기본 퀴즈 데이터 테스트."""

import unittest

import helpers  # noqa: F401  (프로젝트 경로 등록)

from default_quizzes import get_default_quizzes
from quiz import CHOICE_COUNT, Quiz


def sample_dict(**changes):
    data = {"question": "1 + 1은?", "choices": ["1", "2", "3", "4"], "answer": 2, "hint": "짝수"}
    data.update(changes)
    return data


class QuizTest(unittest.TestCase):
    def test_is_correct(self):
        quiz = Quiz.from_dict(sample_dict())
        self.assertTrue(quiz.is_correct(2))
        self.assertFalse(quiz.is_correct(1))
        self.assertEqual(quiz.correct_choice_text(), "2")

    def test_dict_round_trip(self):
        data = sample_dict(question="한글 문제 🎯")
        self.assertEqual(Quiz.from_dict(data).to_dict(), data)

    def test_old_file_without_hint_is_accepted(self):
        data = sample_dict()
        del data["hint"]
        self.assertEqual(Quiz.from_dict(data).hint, "")

    def test_invalid_data_is_rejected(self):
        cases = {
            "not a dict": ["question"],
            "empty question": sample_dict(question="  "),
            "three choices": sample_dict(choices=["1", "2", "3"]),
            "blank choice": sample_dict(choices=["1", "", "3", "4"]),
            "answer 0": sample_dict(answer=0),
            "answer 5": sample_dict(answer=5),
            "answer as text": sample_dict(answer="2"),
            "answer true": sample_dict(answer=True),  # True == 1 이지만 정답 번호로 받지 않는다.
            "hint not text": sample_dict(hint=3),
        }
        for name, data in cases.items():
            with self.subTest(name), self.assertRaises(ValueError):
                Quiz.from_dict(data)


class DefaultQuizzesTest(unittest.TestCase):
    def test_at_least_five_valid_quizzes(self):
        quizzes = get_default_quizzes()
        self.assertGreaterEqual(len(quizzes), 5)  # 미션 요구: 기본 퀴즈 5개 이상
        self.assertEqual(len(quizzes), 8)  # README에 적은 개수
        for quiz in quizzes:
            with self.subTest(question=quiz.question):
                Quiz.from_dict(quiz.to_dict())  # 저장 형식 검사를 통과해야 한다.
                self.assertEqual(len(quiz.choices), CHOICE_COUNT)
                self.assertEqual(len(set(quiz.choices)), CHOICE_COUNT)  # 선택지 중복 없음
                self.assertTrue(quiz.hint)

    def test_questions_are_unique(self):
        questions = [quiz.question for quiz in get_default_quizzes()]
        self.assertEqual(len(questions), len(set(questions)))

    def test_returns_new_objects_each_time(self):
        # 기본 퀴즈를 지워도 다음 호출 결과에 영향이 없어야 한다.
        first = get_default_quizzes()
        first.pop()
        self.assertEqual(len(get_default_quizzes()), 8)


if __name__ == "__main__":
    unittest.main()
