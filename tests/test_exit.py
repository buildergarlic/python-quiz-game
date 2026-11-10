"""실제 프로그램(main.py)을 따로 실행해 종료 경로를 확인한다: 메뉴 7, 입력 종료, Ctrl+C, SIGTERM."""

import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from helpers import PROJECT_ROOT

TIMEOUT = 10


class ExitTest(unittest.TestCase):
    def setUp(self):
        self._folder = tempfile.TemporaryDirectory()
        self.addCleanup(self._folder.cleanup)
        self.state = Path(self._folder.name) / "state.json"
        self.env = dict(os.environ, QUIZ_STATE_PATH=str(self.state), PYTHONIOENCODING="utf-8",
                        PYTHONUNBUFFERED="1", PYTHONDONTWRITEBYTECODE="1")

    def run_game(self, stdin_text):
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "main.py")], input=stdin_text, env=self.env,
            capture_output=True, text=True, encoding="utf-8", timeout=TIMEOUT,
        )
        return result.returncode, result.stdout

    def test_menu_exit(self):
        code, out = self.run_game("7\n")
        self.assertEqual(code, 0)
        self.assertIn("게임을 종료합니다", out)
        self.assertEqual(len(json.loads(self.state.read_text(encoding="utf-8"))["quizzes"]), 8)

    def test_added_quiz_survives_restart(self):
        self.run_game("2\n새 문제\n가\n나\n다\n라\n1\n\n7\n")
        code, out = self.run_game("7\n")
        self.assertEqual(code, 0)
        self.assertIn("퀴즈 9개", out)

    def test_end_of_input_saves_and_exits(self):
        code, out = self.run_game("")  # Ctrl+D / Ctrl+Z 처럼 입력이 끝남
        self.assertEqual(code, 0)
        self.assertIn("데이터를 저장하고 안전하게 종료합니다", out)

    @unittest.skipIf(os.name == "nt", "Windows에는 다른 프로세스에 SIGINT/SIGTERM을 보내는 방법이 없다")
    def test_signals_save_and_exit(self):
        for sig in (signal.SIGINT, signal.SIGTERM):
            with self.subTest(signal=sig.name):
                process = subprocess.Popen(
                    [sys.executable, str(PROJECT_ROOT / "main.py")], stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, env=self.env,
                )
                self.addCleanup(process.kill)
                self._wait_for_menu(process)
                process.send_signal(sig)
                out, _ = process.communicate(timeout=TIMEOUT)
                text = out.decode("utf-8")
                self.assertEqual(process.returncode, 0, text)
                self.assertIn("데이터를 저장하고 안전하게 종료합니다", text)
                self.assertTrue(self.state.exists())

    def _wait_for_menu(self, process):
        """첫 실행 저장(state.json 생성)이 끝나 메뉴 입력을 기다릴 때까지 기다린다."""
        deadline = time.monotonic() + TIMEOUT
        while not self.state.exists():
            if time.monotonic() > deadline:
                self.fail("메뉴가 뜨지 않았습니다.")
            time.sleep(0.05)
        time.sleep(0.3)


if __name__ == "__main__":
    unittest.main()
