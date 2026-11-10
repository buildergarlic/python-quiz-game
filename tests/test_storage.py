"""state.json 저장·불러오기·손상 복구 테스트 (StateStorage, QuizGame.load_state)."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from helpers import typed

from default_quizzes import get_default_quizzes
from quiz import Quiz
from quiz_game import QuizGame
from storage import StateStorage

RECORD = {"played_at": "2026-11-10 12:00:00", "total": 3, "correct": 2, "hints_used": 1, "score": 50}


class StorageTestCase(unittest.TestCase):
    def setUp(self):
        self._folder = tempfile.TemporaryDirectory()
        self.addCleanup(self._folder.cleanup)
        self.path = Path(self._folder.name) / "state.json"
        self.storage = StateStorage(self.path)

    def write_raw(self, text):
        self.path.write_text(text, encoding="utf-8")


class SaveLoadTest(StorageTestCase):
    def test_round_trip_keeps_korean_as_utf8(self):
        quizzes = [Quiz("한글 문제 🎯", ["가", "나", "다", "라"], 3, "힌트")]
        self.storage.save(quizzes, 80, [RECORD])

        text = self.path.read_text(encoding="utf-8")
        self.assertIn("한글 문제 🎯", text)  # 한 같은 이스케이프 없이 그대로 저장
        status, data = self.storage.load()
        self.assertEqual(status, "loaded")
        self.assertEqual(data["quizzes"][0].to_dict(), quizzes[0].to_dict())
        self.assertEqual(data["best_score"], 80)
        self.assertEqual(data["history"], [RECORD])

    def test_save_leaves_no_temp_file(self):
        self.storage.save(get_default_quizzes(), None, [])
        self.assertTrue(self.path.exists())
        self.assertFalse(self.storage.temp_path.exists())

    def test_save_creates_missing_folder(self):
        storage = StateStorage(self.path.parent / "data" / "state.json")
        storage.save(get_default_quizzes(), None, [])
        self.assertEqual(storage.load()[0], "loaded")

    def test_failed_write_keeps_old_file(self):
        self.storage.save(get_default_quizzes(), 70, [])
        before = self.path.read_bytes()

        class NotJson:
            pass

        with self.assertRaises(TypeError):  # 기록에 JSON으로 못 바꾸는 값이 섞여 저장이 중간에 실패
            self.storage.save(get_default_quizzes(), 90, [{"bad": NotJson()}])
        self.assertEqual(self.path.read_bytes(), before)  # 원본은 그대로 남는다.

    def test_large_data_round_trip(self):
        quizzes = [Quiz(f"문제 {n}", ["가", "나", "다", "라"], n % 4 + 1, "") for n in range(1000)]
        self.storage.save(quizzes, 100, [RECORD] * 1000)
        status, data = self.storage.load()
        self.assertEqual(status, "loaded")
        self.assertEqual(len(data["quizzes"]), 1000)
        self.assertEqual(data["quizzes"][999].question, "문제 999")


class LoadStatusTest(StorageTestCase):
    def test_missing(self):
        self.assertEqual(self.storage.load(), ("missing", None))

    def test_broken_json_is_corrupted(self):
        self.write_raw('{"quizzes": [')
        self.assertEqual(self.storage.load(), ("corrupted", None))

    def test_wrong_structure_is_corrupted(self):
        cases = {
            "list at top": "[]",
            "no quizzes": '{"best_score": 10}',
            "bool answer": json.dumps({"quizzes": [
                {"question": "q", "choices": ["a", "b", "c", "d"], "answer": True}]}),
            "score over 100": '{"quizzes": [], "best_score": 101}',
            "bool score": '{"quizzes": [], "best_score": true}',
            "history not list": '{"quizzes": [], "history": {}}',
            "bad record": '{"quizzes": [], "history": [{"played_at": "x", "total": "3"}]}',
        }
        for name, text in cases.items():
            with self.subTest(name):
                self.write_raw(text)
                self.assertEqual(self.storage.load(), ("corrupted", None))

    def test_old_file_without_history(self):
        self.write_raw('{"quizzes": [], "best_score": null}')
        status, data = self.storage.load()
        self.assertEqual(status, "loaded")
        self.assertEqual(data["history"], [])

    def test_unreadable_path_is_error(self):
        self.path.mkdir()  # state.json 자리에 폴더가 있으면 파일로 열 수 없다.
        self.assertEqual(self.storage.load(), ("error", None))

    def test_backup_copies_original(self):
        self.write_raw("{broken")
        self.assertTrue(self.storage.backup_corrupted_file())
        self.assertEqual(self.storage.backup_path.read_text(encoding="utf-8"), "{broken")


class GameLoadStateTest(StorageTestCase):
    def start_game(self):
        game = QuizGame(self.storage)
        with typed() as output:
            message = game.load_state()
        return game, message + output.getvalue()

    def test_first_run_creates_file_with_defaults(self):
        game, message = self.start_game()
        self.assertIn("기본 퀴즈 8개로 시작", message)
        self.assertEqual(len(game.quizzes), 8)
        self.assertEqual(self.storage.load()[0], "loaded")

    def test_saved_data_is_restored(self):
        self.storage.save([Quiz("내 문제", ["a", "b", "c", "d"], 1)], 90, [RECORD])
        game, message = self.start_game()
        self.assertIn("퀴즈 1개, 최고점수 90점", message)
        self.assertEqual(game.history, [RECORD])

    def test_corrupted_file_is_backed_up_and_reset(self):
        self.write_raw("{broken")
        game, message = self.start_game()
        self.assertIn("손상되어 기본 퀴즈 데이터로 복구", message)
        self.assertEqual(self.storage.backup_path.read_text(encoding="utf-8"), "{broken")
        self.assertEqual(self.storage.load()[0], "loaded")  # 새 파일로 다시 저장됨
        self.assertTrue(game.can_save)

    def test_unreadable_file_is_never_overwritten(self):
        self.path.mkdir()
        game, message = self.start_game()
        self.assertIn("이번 실행에서는 저장하지 않습니다", message)
        self.assertFalse(game.can_save)
        self.assertFalse(game.save_state())
        self.assertTrue(self.path.is_dir())

    @unittest.skipIf(os.name == "nt", "Windows에서는 폴더 권한으로 쓰기를 막는 방식이 다르다")
    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root는 권한과 상관없이 쓸 수 있다")
    def test_save_failure_shows_message_and_game_continues(self):
        game, _ = self.start_game()
        os.chmod(self.path.parent, 0o500)  # 폴더를 읽기 전용으로 → 임시 파일을 만들 수 없음
        self.addCleanup(os.chmod, self.path.parent, 0o700)
        with typed() as output:
            self.assertFalse(game.save_state())
        self.assertIn("데이터를 파일에 저장하지 못했습니다", output.getvalue())


if __name__ == "__main__":
    unittest.main()
