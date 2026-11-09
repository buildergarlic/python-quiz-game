"""state.json 파일 저장/불러오기를 담당하는 StateStorage 클래스."""

import json
import os
import shutil
from pathlib import Path

from quiz import Quiz


RECORD_NUMBER_KEYS = ("total", "correct", "hints_used", "score")  # 게임 기록의 숫자 항목


class StateStorage:
    """퀴즈 목록, 최고 점수, 게임 기록을 JSON 파일(state.json)에 저장하고 불러온다."""

    def __init__(self, path):
        self.path = Path(path)
        self.backup_path = self.path.with_name(self.path.name + ".bak")  # 손상된 파일 백업
        self.temp_path = self.path.with_name(self.path.name + ".tmp")  # 안전한 저장용 임시 파일

    def load(self):
        """state.json을 읽어 (상태, 데이터) 튜플을 반환한다.

        - ("loaded", {"quizzes": [...], "best_score": ..., "history": [...]}) : 정상적으로 읽음
        - ("missing", None)   : 파일이 없음 (첫 실행)
        - ("corrupted", None) : JSON 문법이 깨졌거나 데이터 구조가 올바르지 않음
        - ("error", None)     : 권한 문제 등으로 파일을 읽지 못함
        """
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                raw = json.load(file)
        except FileNotFoundError:
            return "missing", None
        except (json.JSONDecodeError, UnicodeDecodeError):
            return "corrupted", None
        except OSError:
            return "error", None

        try:
            return "loaded", self._parse(raw)
        except ValueError:
            return "corrupted", None

    def save(self, quizzes, best_score, history):
        """퀴즈 목록, 최고 점수, 게임 기록을 state.json에 UTF-8로 저장한다. 실패하면 OSError가 발생한다.

        임시 파일에 먼저 끝까지 쓴 뒤 os.replace()로 한 번에 바꿔 끼운다.
        저장 도중 프로그램이 멈춰도 기존 state.json이 반쯤 쓰인 채로 망가지지 않는다.
        """
        data = {
            "quizzes": [quiz.to_dict() for quiz in quizzes],
            "best_score": best_score,
            "history": history,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)  # 저장 폴더가 없으면 만든다.
        with open(self.temp_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        os.replace(self.temp_path, self.path)

    def backup_corrupted_file(self):
        """손상된 state.json을 state.json.bak으로 복사해 둔다. 성공하면 True를 반환한다."""
        try:
            shutil.copyfile(self.path, self.backup_path)
        except OSError:
            return False
        return True

    def _parse(self, raw):
        """JSON에서 읽은 값을 검사하고 프로그램에서 쓰는 형태로 바꾼다. 잘못되면 ValueError."""
        if not isinstance(raw, dict):
            raise ValueError("최상위 데이터가 딕셔너리가 아닙니다.")
        if not isinstance(raw.get("quizzes"), list):
            raise ValueError("quizzes 목록이 없습니다.")

        quizzes = []
        for item in raw["quizzes"]:
            quizzes.append(Quiz.from_dict(item))

        best_score = raw.get("best_score")
        if best_score is not None and not is_valid_score(best_score):
            raise ValueError("best_score 값이 올바르지 않습니다.")

        # 기록 기능 이전에 저장한 파일에는 history가 없을 수 있으므로 빈 목록으로 시작한다.
        history = raw.get("history", [])
        if not isinstance(history, list):
            raise ValueError("history가 목록이 아닙니다.")
        for record in history:
            if not is_valid_record(record):
                raise ValueError("history에 형식이 올바르지 않은 기록이 있습니다.")

        return {"quizzes": quizzes, "best_score": best_score, "history": history}


def is_valid_score(value):
    """0~100 사이의 정수 점수인지 확인한다. (True/False는 제외)"""
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 100


def is_valid_record(record):
    """게임 기록 한 개(딕셔너리)의 형식이 올바른지 확인한다."""
    if not isinstance(record, dict) or not isinstance(record.get("played_at"), str):
        return False
    for key in RECORD_NUMBER_KEYS:
        value = record.get(key)
        if isinstance(value, bool) or not isinstance(value, int):
            return False
    return True
