# 나만의 퀴즈 게임 — 어떤 OS(Windows/macOS/Linux)에서도 같은 Python 환경으로 실행하기 위한 이미지
#
# 빌드: docker build -t python-quiz-game .
# 실행: docker run --rm -it -v quiz-data:/data python-quiz-game

# 파이썬 버전을 정확히 고정해 누가 빌드해도 같은 환경이 되게 한다.
# 다른 버전 확인: docker build --build-arg PYTHON_VERSION=3.10 -t python-quiz-game:py3.10 .
ARG PYTHON_VERSION=3.12.16
FROM python:${PYTHON_VERSION}-slim

# PYTHONUNBUFFERED      : 출력을 바로 화면에 보낸다 (입력 프롬프트가 늦게 보이지 않게)
# PYTHONDONTWRITEBYTECODE: __pycache__ 파일을 만들지 않는다
# PYTHONIOENCODING, LANG : 한글·이모지 입출력을 UTF-8로 고정한다
# QUIZ_STATE_PATH        : 퀴즈·점수 데이터를 볼륨(/data)에 저장해 컨테이너를 지워도 남게 한다
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8 \
    QUIZ_STATE_PATH=/data/state.json

WORKDIR /app

# 관리자(root)가 아닌 일반 사용자(uid 1000)로 실행하고, 데이터 폴더를 그 사용자에게 준다.
RUN useradd --create-home --uid 1000 quiz \
    && mkdir -p /data \
    && chown quiz:quiz /data

# 게임 코드만 복사한다. (외부 라이브러리가 없어서 pip 설치 단계가 없다)
COPY --chown=quiz:quiz *.py ./

USER quiz

# docker stop을 Ctrl+C와 같은 신호(SIGINT)로 보내 '저장 후 안전 종료'가 동작하게 한다.
STOPSIGNAL SIGINT

CMD ["python", "main.py"]
