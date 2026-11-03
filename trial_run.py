"""
trial_run.py
------------
Basic trial for the memory model only -- no LLM, no FastAPI, no RAG.
Simulates ONE user ("userA") who is strong in Python and weak in
everything else, across 40 trials, and prints what the system decides
and remembers at each step.

Run:
    cd ai-engine
    python3 trial_run.py
"""

import random

from app.db.database import reset_db, get_connection
from app.core.memory_store import (
    get_or_create_user,
    get_user_memory,
    decide_next_question,
    record_attempt,
)

LANGUAGES = ["python", "javascript", "java", "cpp"]

# Simulated ground truth: how likely userA is to answer correctly in each
# language. This stands in for a real person answering real questions.
TRUE_SKILL = {
    "python": 0.9,       # strong
    "javascript": 0.3,   # weak
    "java": 0.25,        # weak
    "cpp": 0.2,          # weakest
}


def simulate_answer(language: str) -> bool:
    return random.random() < TRUE_SKILL[language]


def main():
    reset_db()
    conn = get_connection()

    user_id = get_or_create_user(conn, firebase_uid="trial-userA", name="UserA")

    print("=" * 60)
    print("TRIAL: profiling phase (trials 1-30) -- should be random,")
    print("always beginner difficulty, across all 4 languages.")
    print("=" * 60)

    language_counts = {lang: 0 for lang in LANGUAGES}

    for trial in range(1, 41):
        decision = decide_next_question(conn, user_id, trial, LANGUAGES)
        lang = decision["language"]
        difficulty = decision["difficulty"]
        phase = decision["phase"]
        language_counts[lang] += 1

        is_correct = simulate_answer(lang)
        record_attempt(conn, user_id, lang, trial, difficulty, is_correct)

        marker = "correct" if is_correct else "wrong"
        if trial <= 5 or trial in (30, 31, 32, 40):
            print(
                f"trial {trial:>2} [{phase:>9}] -> language={lang:<10} "
                f"difficulty={difficulty:<2} answer={marker}"
            )

    print()
    print("How many times each language was picked (1-40):")
    for lang, count in language_counts.items():
        print(f"  {lang:<12} picked {count} times")

    print()
    print("Final memory state (this is what skill_levels now holds):")
    for row in get_user_memory(conn, user_id):
        acc = row["correct_count"] / row["attempts_count"] if row["attempts_count"] else 0
        print(
            f"  {row['language']:<12} level={row['level']:<2} "
            f"attempts={row['attempts_count']:<3} correct={row['correct_count']:<3} "
            f"accuracy={acc:.0%}"
        )

    conn.close()
    print()
    print("Expect: python should trend to a higher level, and after trial 30")
    print("the weaker languages (js/java/cpp) should get picked more often")
    print("than python, since selection weights toward weakness.")


if __name__ == "__main__":
    main()
