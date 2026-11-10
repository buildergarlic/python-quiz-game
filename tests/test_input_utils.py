"""입력 검증 함수(input_utils.py) 테스트."""

import unittest

from helpers import typed

from input_utils import parse_int, read_int, read_text, read_yes_no


class ParseIntTest(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(parse_int("3", 1, 7), (3, None))

    def test_strips_spaces(self):
        self.assertEqual(parse_int("  1 ", 1, 7), (1, None))

    def test_range_edges_are_included(self):
        self.assertEqual(parse_int("1", 1, 7)[0], 1)
        self.assertEqual(parse_int("7", 1, 7)[0], 7)
        self.assertEqual(parse_int("0", 0, 5)[0], 0)  # 삭제 화면의 '취소는 0'

    def test_empty_input(self):
        number, error = parse_int("   ", 1, 7)
        self.assertIsNone(number)
        self.assertIn("비어 있습니다", error)

    def test_not_a_number(self):
        for raw in ("abc", "1.5", "일", "1 2"):
            with self.subTest(raw=raw):
                number, error = parse_int(raw, 1, 7)
                self.assertIsNone(number)
                self.assertIn("잘못된 입력", error)

    def test_out_of_range(self):
        for raw in ("0", "8", "-1", "100"):
            with self.subTest(raw=raw):
                number, error = parse_int(raw, 1, 7)
                self.assertIsNone(number)
                self.assertIn("1-7 사이", error)


class ReadFunctionsTest(unittest.TestCase):
    def test_read_int_asks_again_until_valid(self):
        with typed("", "abc", "9", " 2 ") as output:
            self.assertEqual(read_int("선택: ", 1, 7), 2)
        self.assertEqual(output.getvalue().count("⚠️"), 3)  # 잘못된 입력 3번마다 안내

    def test_read_text_rejects_blank(self):
        with typed("", "   ", "  문제  "):
            self.assertEqual(read_text("문제: "), "문제")

    def test_read_yes_no_accepts_korean_keyboard(self):
        for raw, expected in (("y", True), ("YES", True), ("ㅛ", True), ("n", False), ("ㅜ", False)):
            with self.subTest(raw=raw), typed(raw):
                self.assertIs(read_yes_no("삭제할까요? "), expected)

    def test_read_yes_no_asks_again(self):
        with typed("네", "", "y") as output:
            self.assertTrue(read_yes_no("삭제할까요? "))
        self.assertEqual(output.getvalue().count("y 또는 n"), 2)

    def test_interrupt_is_not_swallowed(self):
        # Ctrl+C / 입력 종료는 여기서 잡지 않고 QuizGame.run()까지 올려 보내야 저장 후 종료된다.
        for error in (KeyboardInterrupt, EOFError):
            with self.subTest(error=error.__name__), typed(error()):
                with self.assertRaises(error):
                    read_int("선택: ", 1, 7)


if __name__ == "__main__":
    unittest.main()
