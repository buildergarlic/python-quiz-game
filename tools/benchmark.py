"""퀴즈가 1,000개 이상으로 늘어났을 때 현재 구조(state.json 한 파일)의 한계를 측정한다.

실행 방법 (프로젝트 루트에서):
    python tools/benchmark.py              # 1,000 / 10,000 / 100,000개
    python tools/benchmark.py 1000 5000    # 원하는 개수만

- 실제 게임 코드(Quiz, StateStorage, QuizGame)를 그대로 사용한다.
- 임시 폴더에서만 읽고 쓰므로 내 state.json은 건드리지 않는다.
- 비교용으로 표준 라이브러리 sqlite3에 같은 데이터를 넣어 'DB로 옮기면 어떻게 달라지는지'도 잰다.
- 시간은 PC마다 다르므로 절대값보다 '개수가 10배일 때 몇 배가 되는지'를 보면 된다.
"""

import contextlib
import io
import json
import os
import random
import sqlite3
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from quiz import Quiz  # noqa: E402  (경로를 추가한 뒤에 가져와야 한다)
from quiz_game import QuizGame  # noqa: E402
from storage import StateStorage  # noqa: E402

DEFAULT_SIZES = (1_000, 10_000, 100_000)
REPEAT = 3  # 각 측정을 3번 해서 가장 빠른 값을 쓴다 (다른 프로그램의 간섭을 줄이기 위해)


def make_quizzes(count):
    """실제 퀴즈와 비슷한 길이(문제 약 40자, 선택지 4개, 힌트)의 퀴즈를 count개 만든다."""
    quizzes = []
    for number in range(count):
        quizzes.append(Quiz(
            f"{number}번 문제: 다음 중 Python 리스트 메서드 append의 동작으로 옳은 것은?",
            [f"보기 A-{number}", f"보기 B-{number}", f"보기 C-{number}", f"보기 D-{number}"],
            number % 4 + 1,
            "리스트 끝에 요소 하나를 추가합니다.",
        ))
    return quizzes


def best_time(func, repeat=REPEAT):
    """func를 repeat번 실행해 가장 짧은 실행 시간(초)과 마지막 반환값을 돌려준다."""
    best, result = None, None
    for _ in range(repeat):
        start = time.perf_counter()
        result = func()
        elapsed = time.perf_counter() - start
        best = elapsed if best is None else min(best, elapsed)
    return best, result


def peak_memory(func):
    """func 실행 중 파이썬이 사용한 메모리의 최댓값(바이트)을 잰다."""
    tracemalloc.start()
    func()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


def measure_json(count, folder):
    """현재 방식(state.json 하나에 전부 저장)을 측정한다."""
    quizzes = make_quizzes(count)
    history = [
        {"played_at": "2026-11-10 12:00:00", "total": 10, "correct": 7, "hints_used": 1, "score": 65}
        for _ in range(count)
    ]
    storage = StateStorage(Path(folder) / "state.json")

    save_sec, _ = best_time(lambda: storage.save(quizzes, 80, history))
    load_sec, (status, data) = best_time(storage.load)
    assert status == "loaded" and len(data["quizzes"]) == count
    load_peak = peak_memory(storage.load)
    file_size = os.path.getsize(storage.path)
    compact_size = len(json.dumps(
        {"quizzes": [quiz.to_dict() for quiz in quizzes], "best_score": 80, "history": history},
        ensure_ascii=False,
    ).encode("utf-8"))

    # '3. 퀴즈 목록' 화면: 실제 메서드를 실행하고 출력은 버린다.
    game = QuizGame(storage)
    game.quizzes = quizzes
    output = io.StringIO()
    list_sec, _ = best_time(lambda: _list_quietly(game, output))
    list_lines = output.getvalue().count("\n") // REPEAT

    keyword = f"{count - 1}번 문제"  # 맨 마지막 문제 = 가장 오래 걸리는 경우
    search_sec, found = best_time(lambda: [q for q in quizzes if keyword in q.question])
    assert len(found) == 1
    sample_sec, _ = best_time(lambda: random.sample(quizzes, 10))
    copies = [quizzes.copy() for _ in range(REPEAT)]  # 복사 시간은 빼고 pop(0)만 잰다.
    delete_sec, _ = best_time(lambda: copies.pop().pop(0))

    return {
        "count": count,
        "file_mb": file_size / 1_000_000,
        "compact_mb": compact_size / 1_000_000,
        "save_ms": save_sec * 1000,
        "load_ms": load_sec * 1000,
        "load_peak_mb": load_peak / 1_000_000,
        "list_ms": list_sec * 1000,
        "list_lines": list_lines,
        "search_ms": search_sec * 1000,
        "sample_ms": sample_sec * 1000,
        "delete_ms": delete_sec * 1000,
    }


def _list_quietly(game, output):
    with contextlib.redirect_stdout(output):
        game.list_quizzes()


def measure_sqlite(count, folder):
    """비교용: 같은 퀴즈를 SQLite 표에 넣었을 때 '한 개 추가'와 '검색' 비용을 잰다."""
    path = Path(folder) / "quiz.db"
    connection = sqlite3.connect(path)
    connection.execute(
        "CREATE TABLE quiz (id INTEGER PRIMARY KEY, question TEXT, c1 TEXT, c2 TEXT, c3 TEXT, c4 TEXT,"
        " answer INTEGER, hint TEXT)"
    )
    rows = [(q.question, *q.choices, q.answer, q.hint) for q in make_quizzes(count)]
    with connection:
        connection.executemany(
            "INSERT INTO quiz (question, c1, c2, c3, c4, answer, hint) VALUES (?, ?, ?, ?, ?, ?, ?)", rows
        )

    def add_one():
        with connection:  # 트랜잭션 1번 = 디스크에 확정 저장
            connection.execute(
                "INSERT INTO quiz (question, c1, c2, c3, c4, answer, hint) VALUES (?, ?, ?, ?, ?, ?, ?)",
                rows[0],
            )

    add_sec, _ = best_time(add_one)
    keyword = f"{count - 1}번 문제%"
    like_sec, _ = best_time(lambda: connection.execute(
        "SELECT id FROM quiz WHERE question LIKE ?", (keyword,)).fetchall())
    page_sec, _ = best_time(lambda: connection.execute(
        "SELECT id, question FROM quiz ORDER BY id LIMIT 20 OFFSET ?", (count // 2,)).fetchall())
    sample_sec, _ = best_time(lambda: connection.execute(
        "SELECT * FROM quiz WHERE id IN (SELECT id FROM quiz ORDER BY RANDOM() LIMIT 10)").fetchall())
    connection.close()
    return {
        "count": count,
        "db_mb": os.path.getsize(path) / 1_000_000,
        "add_ms": add_sec * 1000,
        "like_ms": like_sec * 1000,
        "page_ms": page_sec * 1000,
        "sample_ms": sample_sec * 1000,
    }


def print_table(headers, rows):
    print("| " + " | ".join(headers) + " |")
    print("|" + "---|" * len(headers))
    for row in rows:
        print("| " + " | ".join(row) + " |")


def main():
    sizes = [int(arg) for arg in sys.argv[1:]] or list(DEFAULT_SIZES)
    print(f"Python {sys.version.split()[0]} / {sys.platform} / 각 값은 {REPEAT}회 중 최솟값\n")
    json_rows, sqlite_rows = [], []
    for count in sizes:
        with tempfile.TemporaryDirectory() as folder:
            print(f"측정 중: 퀴즈 {count:,}개 ...", file=sys.stderr)
            json_rows.append(measure_json(count, folder))
            sqlite_rows.append(measure_sqlite(count, folder))

    print("## 현재 구조: state.json 한 파일 (퀴즈 N개 + 게임 기록 N개)\n")
    print_table(
        ["퀴즈 수", "파일 크기", "들여쓰기 없이", "저장(추가·삭제·풀이마다)", "불러오기(시작 시)",
         "불러오기 최대 메모리", "목록 출력", "목록 줄 수", "검색(전체 훑기)", "10문제 뽑기", "맨 앞 삭제"],
        [[f"{r['count']:,}", f"{r['file_mb']:.2f} MB", f"{r['compact_mb']:.2f} MB", f"{r['save_ms']:.1f} ms",
          f"{r['load_ms']:.1f} ms", f"{r['load_peak_mb']:.1f} MB", f"{r['list_ms']:.1f} ms",
          f"{r['list_lines']:,}", f"{r['search_ms']:.2f} ms", f"{r['sample_ms']:.3f} ms",
          f"{r['delete_ms']:.3f} ms"] for r in json_rows],
    )
    print("\n## 비교: SQLite(표준 라이브러리 sqlite3) 표에 같은 퀴즈 N개\n")
    print_table(
        ["퀴즈 수", "DB 크기", "1개 추가(저장 포함)", "문제 검색(LIKE)", "20개씩 페이지 조회", "10문제 무작위 뽑기"],
        [[f"{r['count']:,}", f"{r['db_mb']:.2f} MB", f"{r['add_ms']:.2f} ms", f"{r['like_ms']:.2f} ms",
          f"{r['page_ms']:.3f} ms", f"{r['sample_ms']:.2f} ms"] for r in sqlite_rows],
    )


if __name__ == "__main__":
    main()
