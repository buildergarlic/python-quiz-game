# 🎯 나만의 퀴즈 게임 (Python Quiz Game)

터미널에서 동작하는 4지선다 퀴즈 게임입니다.
메뉴에서 번호를 골라 퀴즈를 풀고, 직접 퀴즈를 추가·삭제하고, 최고 점수와 게임 기록을 확인할 수 있습니다.
프로그램을 종료했다가 다시 실행해도 퀴즈와 점수는 `state.json` 파일에 저장되어 그대로 남아 있습니다.

## 1. 프로젝트 개요

| 항목 | 내용 |
|---|---|
| 형태 | Python 콘솔(터미널) 프로그램 |
| 개발 환경 | Python 3.10 이상 (3.10, 3.13에서 동작 확인), 외부 라이브러리 없음 (표준 라이브러리만 사용) |
| 핵심 구조 | `Quiz`(문제 1개), `QuizGame`(게임 흐름), `StateStorage`(파일 저장) 3개 클래스로 역할 분리 |
| 데이터 저장 | 프로젝트 루트의 `state.json` (UTF-8 JSON) |
| 버전 관리 | Git 기능 단위 커밋 + 기능 브랜치(`feature/*`) 작업 후 `main`에 병합 |

## 2. 퀴즈 주제와 선정 이유

**주제: Python & Git 기초**

- **만드는 과정이 곧 복습이다.** 이 미션에서 배우는 자료형, 반복문, 클래스, JSON, 예외 처리, Git 명령어를 문제로 만들었습니다. 좋은 4지선다 문제를 내려면 정답뿐 아니라 오답 선택지가 *왜* 틀렸는지도 알아야 해서, 문제를 만드는 과정에서 개념을 한 번 더 정리할 수 있었습니다.
- **코드와 퀴즈가 서로를 설명한다.** `int('abc')`가 `ValueError`를 내는 것(숫자 입력 검증), `None`이 JSON에서 `null`로 저장되는 것(`best_score`) 등 이 게임을 만들면서 실제로 마주친 내용을 문제로 넣었습니다.
- **함께 쓸 수 있다.** 같은 과정을 밟는 동료들도 바로 풀어 보며 복습할 수 있는 주제입니다.

## 3. 실행 방법

```bash
# 1) 저장소 복제
git clone https://github.com/<GitHub-아이디>/python-quiz-game.git
cd python-quiz-game

# 2) 실행 (Windows)
python main.py

# 2) 실행 (macOS / Linux)
python3 main.py
```

- Python 버전 확인: `python --version` (3.10 이상)
- 설치할 패키지는 없습니다.
- 처음 실행하면 기본 퀴즈 8개로 시작하고 `state.json`이 자동으로 만들어집니다.

## 4. 기능 목록

### 메뉴

| 번호 | 메뉴 | 설명 |
|:-:|---|---|
| 1 | 퀴즈 풀기 | 풀 문제 수를 고르면 **무작위 순서**로 출제합니다. 정답/오답을 바로 알려 주고, 다 풀면 결과와 최고 점수 갱신 여부를 보여 줍니다. |
| 2 | 퀴즈 추가 | 문제, 선택지 4개, 정답 번호(1-4), 힌트(선택)를 입력받아 등록하고 바로 저장합니다. |
| 3 | 퀴즈 목록 | 등록된 퀴즈를 번호와 함께 보여 줍니다. (💡 = 힌트 있음) |
| 4 | 점수 확인 | 최고 점수와 그 점수를 낸 게임의 정답 수·일시를 보여 줍니다. |
| 5 | 퀴즈 삭제 | 번호로 퀴즈를 골라 확인(y/n) 후 삭제하고 저장합니다. (0 = 취소) |
| 6 | 게임 기록 | 최근 10회 게임 기록(일시, 문제 수, 정답 수, 힌트 사용, 점수)을 최신순으로 보여 줍니다. |
| 7 | 종료 | 데이터를 저장하고 종료합니다. |

### 보너스 과제 구현

- [x] 랜덤 출제 — `random.sample()`로 원본 목록은 그대로 두고 무작위로 뽑기
- [x] 문제 수 선택 — 퀴즈 시작 시 1 ~ 전체 문제 수 중 선택
- [x] 힌트 기능 — 풀이 중 `h` 입력 시 힌트 표시, 힌트를 보고 맞힌 문제는 **절반 점수**
- [x] 퀴즈 삭제 기능
- [x] 점수 기록 히스토리 — 모든 게임 기록을 `state.json`에 저장

### 점수 계산

- 100점 만점, 문제당 배점 = `100 / 푼 문제 수`
- 힌트 없이 맞히면 배점 전부, 힌트를 보고 맞히면 배점의 50%, 틀리면 0점
- 예) 3문제 중 1개는 그냥 맞히고 1개는 힌트를 보고 맞히고 1개는 틀림 → (1 + 0.5 + 0) / 3 × 100 = **50점**
- 최고 점수는 이 점수(0~100) 기준으로 비교하며, 기존 최고 점수보다 **높을 때만** 갱신합니다.

### 입력 / 예외 처리

| 상황 | 처리 |
|---|---|
| 앞뒤 공백 (`" 1 "`) | 공백을 제거하고 `1`로 처리 |
| 숫자가 아님 (`abc`) | 안내 메시지 출력 후 다시 입력 |
| 범위 밖 숫자 (메뉴 `9`, 정답 `0`) | 안내 메시지 출력 후 다시 입력 |
| 빈 입력 (그냥 Enter) | 안내 메시지 출력 후 다시 입력 |
| 빈 문제/선택지, 중복 선택지 | 안내 메시지 출력 후 다시 입력 |
| `Ctrl+C` (KeyboardInterrupt), `Ctrl+D`/`Ctrl+Z` (EOFError) | 안내 메시지 → 데이터 저장 → 정상 종료 |
| `state.json` 없음 (첫 실행) | 기본 퀴즈 8개로 시작하고 파일 생성 |
| `state.json` 손상 (JSON 문법 오류, 필드 형식 오류) | `state.json.bak`으로 백업한 뒤 기본 데이터로 복구 |
| `state.json` 읽기 불가 (권한 등) | 기본 퀴즈로 시작하되, 원본을 덮어쓰지 않도록 그 실행에서는 저장하지 않음 |
| 저장 실패 (디스크·권한 문제) | 안내 메시지를 보여 주고 게임은 계속 진행 |

## 5. 파일 구조

```
python-quiz-game/
├── main.py              # 실행 진입점: StateStorage와 QuizGame을 만들어 게임 시작
├── quiz.py              # Quiz 클래스: 퀴즈 1문제 (출력, 정답 확인, 딕셔너리 변환/검증)
├── quiz_game.py         # QuizGame 클래스: 메뉴와 게임 전체 흐름 (풀기/추가/목록/점수/삭제/기록)
├── storage.py           # StateStorage 클래스: state.json 읽기·쓰기·형식 검증·백업
├── input_utils.py       # 공통 입력 함수: 숫자/문자열/y·n 입력 검증
├── default_quizzes.py   # 기본 퀴즈 8문제 (Python & Git 기초)
├── docs/
│   └── screenshots/     # 실행 화면 캡처
├── .gitignore
├── README.md
└── state.json           # 실행하면 자동 생성 (Git에는 올리지 않음)
```

### 클래스 역할

```
main.py
  └─ QuizGame(storage)            게임 진행 담당 — "무엇을 할지"
       ├─ quizzes: [Quiz, ...]    문제 데이터 — "문제 하나가 할 줄 아는 것"
       ├─ storage: StateStorage   파일 담당 — "어떻게 저장할지"
       └─ input_utils 함수들       입력 검증 담당
```

- `QuizGame`은 파일이 어떤 형식으로 저장되는지 몰라도 되고, `StateStorage`는 게임 규칙을 몰라도 됩니다. 저장 방식을 바꾸더라도 `storage.py`만 고치면 됩니다.

## 6. 데이터 파일 설명 (`state.json`)

| 항목 | 내용 |
|---|---|
| 경로 | 프로젝트 루트 (`main.py`와 같은 폴더). `main.py` 위치를 기준으로 경로를 만들기 때문에 어느 폴더에서 실행해도 같은 파일을 사용합니다. |
| 역할 | 퀴즈 목록, 최고 점수, 게임 기록을 저장해 프로그램을 다시 실행해도 유지되게 합니다. |
| 인코딩 | UTF-8 (`ensure_ascii=False`로 한글을 그대로 저장) |
| 저장 시점 | 첫 실행, 퀴즈 추가·삭제, 퀴즈 풀이 종료, 프로그램 종료(중단 포함) |
| Git 관리 | 각자 PC의 플레이 데이터이고 실행할 때마다 바뀌므로 `.gitignore`로 제외합니다. |

### 스키마

```json
{
    "quizzes": [
        {
            "question": "print(type(3.14))의 출력 결과는?",
            "choices": ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'double'>"],
            "answer": 2,
            "hint": "소수점이 있는 수를 '부동소수점(floating point) 수'라고 부릅니다."
        }
    ],
    "best_score": 80,
    "history": [
        {
            "played_at": "2026-11-07 14:03:12",
            "total": 5,
            "correct": 4,
            "hints_used": 0,
            "score": 80
        }
    ]
}
```

| 키 | 타입 | 설명 |
|---|---|---|
| `quizzes` | list | 퀴즈 목록 (필수) |
| `quizzes[].question` | str | 문제 (빈 문자열 불가) |
| `quizzes[].choices` | list[str] | 선택지 4개 |
| `quizzes[].answer` | int | 정답 번호 1~4 (선택지 순서 기준) |
| `quizzes[].hint` | str | 힌트, 없으면 `""` (생략 가능) |
| `best_score` | int 또는 null | 최고 점수 0~100, 아직 풀지 않았으면 `null` |
| `history` | list | 게임 기록 (생략 가능, 오래된 기록부터 순서대로) |
| `history[].played_at` | str | 게임을 마친 일시 `YYYY-MM-DD HH:MM:SS` |
| `history[].total` / `correct` | int | 푼 문제 수 / 맞힌 문제 수 |
| `history[].hints_used` | int | 힌트를 본 문제 수 |
| `history[].score` | int | 그 게임의 점수 |

### 함께 생기는 파일

- `state.json.bak` — `state.json`이 손상되었을 때 복구 직전에 원본을 복사해 둔 백업 파일
- `state.json.tmp` — 저장할 때 잠깐 쓰는 임시 파일. 내용을 끝까지 쓴 뒤 `os.replace()`로 `state.json`과 교체하므로, 저장 도중 프로그램이 멈춰도 기존 파일이 반쯤 쓰인 채로 망가지지 않습니다.

## 7. 실행 화면

| 메뉴 / 잘못된 입력 처리 | 퀴즈 추가 |
|---|---|
| ![메뉴](docs/screenshots/menu.png) | ![퀴즈 추가](docs/screenshots/add_quiz.png) |

| 퀴즈 풀기 (힌트·오답 포함) | 퀴즈 목록 |
|---|---|
| ![퀴즈 풀기](docs/screenshots/play.png) | ![퀴즈 목록](docs/screenshots/list.png) |

| 재실행 후 불러오기 + 점수 확인 | 게임 기록 | Ctrl+C 안전 종료 |
|---|---|---|
| ![점수 확인](docs/screenshots/score.png) | ![게임 기록](docs/screenshots/history.png) | ![안전 종료](docs/screenshots/safe_exit.png) |

## 8. Git 작업 흐름

- **커밋 메시지 규칙**: `Feat`(기능), `Refactor`(구조 개선), `Docs`(문서), `Chore`(설정) + 제목에 변경 요약, 본문에 세부 변경 사항
- **브랜치**
  - `main` — 항상 실행 가능한 상태 유지
  - `feature/play-quiz` — 퀴즈 풀기 기능 개발 후 `main`에 병합
  - `feature/bonus` — 보너스 기능(랜덤, 문제 수 선택, 힌트, 삭제, 기록) 개발 후 `main`에 병합
  - 병합은 `git merge --no-ff`로 수행해 `git log --graph`에서 브랜치 작업 흔적이 보이도록 했습니다.

| 명령어 | 이 프로젝트에서 사용한 곳 |
|---|---|
| `git init` | 프로젝트 폴더를 Git 저장소로 만들기 |
| `git add` / `git commit` | 기능 하나를 완성할 때마다 변경 파일을 스테이징하고 기록 |
| `git checkout -b` / `git checkout` | 기능 브랜치를 만들어 이동, 작업 후 `main`으로 복귀 |
| `git merge` | 기능 브랜치를 `main`에 병합 |
| `git push` | 로컬 커밋을 GitHub 원격 저장소에 업로드 |
| `git clone` | 원격 저장소를 다른 폴더에 복제 (복제 실습) |
| `git pull` | 복제본에서 올린 변경 사항을 기존 작업 폴더로 가져오기 (복제 실습) |
