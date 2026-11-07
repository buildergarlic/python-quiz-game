"""퀴즈 게임 실행 파일.

실행 방법: python main.py
"""

from pathlib import Path

from quiz_game import QuizGame
from storage import StateStorage

# main.py가 있는 폴더(프로젝트 루트)의 state.json을 사용한다.
# 터미널의 현재 위치와 상관없이 항상 같은 파일을 읽고 쓰기 위해 절대 경로로 만든다.
STATE_PATH = Path(__file__).resolve().parent / "state.json"


def main():
    storage = StateStorage(STATE_PATH)
    game = QuizGame(storage)
    game.run()


if __name__ == "__main__":
    main()
