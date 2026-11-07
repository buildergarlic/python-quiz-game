"""기본 퀴즈 데이터.

주제: Python & Git 기초 — 입학연수에서 배우는 내용을 퀴즈로 복습한다.
처음 실행할 때(state.json이 없을 때)나 파일이 손상되었을 때 이 데이터를 사용한다.
"""

from quiz import Quiz


def get_default_quizzes():
    """기본 퀴즈 목록(Quiz 객체 리스트)을 새로 만들어 반환한다."""
    return [
        Quiz(
            question="다음 중 한 번 만든 뒤 요소를 바꿀 수 없는(immutable) 자료형은?",
            choices=["list", "dict", "tuple", "set"],
            answer=3,
        ),
        Quiz(
            question="print(type(3.14))의 출력 결과는?",
            choices=["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'double'>"],
            answer=2,
        ),
        Quiz(
            question="반복 횟수를 미리 알 수 없고, 조건이 참인 동안 계속 반복할 때 주로 쓰는 문법은?",
            choices=["while", "for", "if", "def"],
            answer=1,
        ),
        Quiz(
            question="클래스로 객체를 만들 때 자동으로 호출되어 속성을 초기화하는 메서드는?",
            choices=["__str__", "__call__", "__init__", "__main__"],
            answer=3,
        ),
        Quiz(
            question="Python의 None을 json.dump()로 저장하면 JSON 파일에는 어떤 값으로 기록될까?",
            choices=["nil", "undefined", "None", "null"],
            answer=4,
        ),
        Quiz(
            question="int('abc')를 실행하면 발생하는 예외(오류)는?",
            choices=["TypeError", "ValueError", "KeyError", "IndexError"],
            answer=2,
        ),
        Quiz(
            question="변경 내용을 로컬 저장소에 하나의 기록(스냅샷)으로 남기는 Git 명령어는?",
            choices=["git add", "git commit", "git push", "git clone"],
            answer=2,
        ),
        Quiz(
            question="원격 저장소의 변경 사항을 가져와 현재 브랜치에 합치는 Git 명령어는?",
            choices=["git pull", "git push", "git init", "git status"],
            answer=1,
        ),
    ]
