"""퀴즈 게임 실행 파일.

실행 방법: python main.py
"""

import os
import signal
from pathlib import Path

from quiz_game import QuizGame
from storage import StateStorage

# 기본값: main.py가 있는 폴더(프로젝트 루트)의 state.json을 사용한다.
# 터미널의 현재 위치와 상관없이 항상 같은 파일을 읽고 쓰기 위해 절대 경로로 만든다.
DEFAULT_STATE_PATH = Path(__file__).resolve().parent / "state.json"

# 환경 변수 QUIZ_STATE_PATH가 있으면 그 경로를 쓴다.
# Docker에서는 컨테이너를 지워도 데이터가 남도록 볼륨 경로(/data/state.json)를 지정한다.
STATE_PATH = Path(os.environ.get("QUIZ_STATE_PATH") or DEFAULT_STATE_PATH)


def handle_terminate(signum, frame):
    """종료 요청(SIGTERM)을 Ctrl+C와 똑같이 처리해 '저장 후 안전 종료'로 끝나게 한다.

    kill 명령이나 서비스 관리자가 보내는 SIGTERM은 처리기가 없으면 저장 없이 바로 종료된다.
    KeyboardInterrupt로 바꿔 올리면 QuizGame.run()이 Ctrl+C와 같은 경로로 저장한 뒤 종료한다.
    저장하는 동안 SIGTERM이 또 오면 저장이 중간에 끊기지 않도록 그 뒤로는 무시한다.
    """
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    raise KeyboardInterrupt


def main():
    signal.signal(signal.SIGTERM, handle_terminate)
    storage = StateStorage(STATE_PATH)
    game = QuizGame(storage)
    game.run()


if __name__ == "__main__":
    main()
