"""테스트에서 함께 쓰는 도구: 프로젝트 경로 등록, 가짜 저장소, 입력 흉내 내기."""

import contextlib
import io
import sys
from pathlib import Path
from unittest import mock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class FakeStorage:
    """파일 대신 메모리에 저장하는 가짜 StateStorage. save() 호출 내용을 기록한다."""

    def __init__(self, load_result=("missing", None)):
        self.load_result = load_result
        self.saved = []  # save()가 받은 (퀴즈 수, 최고 점수, 기록 수) 목록
        self.backup_path = Path("state.json.bak")

    def load(self):
        return self.load_result

    def save(self, quizzes, best_score, history):
        self.saved.append((len(quizzes), best_score, len(history)))

    def backup_corrupted_file(self):
        return True


@contextlib.contextmanager
def typed(*answers):
    """input()이 answers를 순서대로 입력한 것처럼 동작하게 하고, 화면 출력을 모아 돌려준다."""
    output = io.StringIO()
    with mock.patch("builtins.input", side_effect=list(answers)), contextlib.redirect_stdout(output):
        yield output
