"""
trial_run.py
------------
Trial 3: tests the NEW skill_score + assessment pipeline end to end,
with no real typed answers. Two phases:

  1. Fake assessment -- simulates answers across difficulty tiers
     1/2/3 (synthetic, since real tier-2/3 question content doesn't
     exist yet) and scores them via score_assessment(), setting each
     language's starting skill_score.
  2. Adaptive quiz -- simulates 20 more answers through the new
     decide_next_question()/record_attempt() API. No level, no
     trial_number, no profiling phase -- adaptive from question 1,
     since the fake assessment already calibrated the user.

Run:
    cd ai-model
    python3 trial_run.py
"""

import random

from app.db.m_database import reset_db, get_connection
from app.core.m_memory_store import (
    get_or_create_user,
    get_user_memory,
    decide_next_question,
    record_attempt,
)
# pyrefly: ignore[missing-import]
from app.core.m_assessment import score_and_store_assessment

LANGUAGES = ["python", "javascript", "java", "cpp"]

TRUE_SKILL = {
    "python": 0.9,       # strong
    "javascript": 0.3,   # weak
    "java": 0.25,        # weak
    "cpp": 0.2,          # weakest
}


def simulate_answer(language: str) -> bool:
    return random.random() < TRUE_SKILL[language]


def fake_assessment_answers(language: str) -> list:
    """3 questions per tier (1, 2, 3) = 9 per language. Synthetic --
    no real tiered content exists yet, this only exercises the scoring
    math and the plumbing into skill_levels."""
    answers = []
    for difficulty in (1, 2, 3):
        for _ in range(3):
            answers.append({"difficulty": difficulty, "is_correct": simulate_answer(language)})
    return answers


def main():
    reset_db()
    conn = get_connection()
    user_id = get_or_create_user(conn, firebase_uid="trial-userA", name="UserA")

    print("=" * 60)
    print("PHASE 1: fake assessment (synthetic, 9 Qs/language, 3 tiers)")
    print("=" * 60)

    answers_by_language = {lang: fake_assessment_answers(lang) for lang in LANGUAGES}
    initial_scores = score_and_store_assessment(conn, user_id, answers_by_language)
    for lang, score in initial_scores.items():
        print(f"  {lang:<12} initial skill_score = {score}")

    print()
    print("=" * 60)
    print("PHASE 2: adaptive quiz (20 questions, no profiling phase)")
    print("=" * 60)

    language_counts = {lang: 0 for lang in LANGUAGES}
    for i in range(1, 21):
        decision = decide_next_question(conn, user_id, LANGUAGES)
        lang = decision["language"]
        difficulty = decision["difficulty"]
        language_counts[lang] += 1

        is_correct = simulate_answer(lang)
        # pyrefly: ignore[unexpected-keyword]
        record_attempt(conn, user_id, lang, difficulty, is_correct, source="quiz")

        if i <= 5 or i == 20:
            marker = "correct" if is_correct else "wrong"
            print(f"  q{i:>2} -> language={lang:<10} difficulty={difficulty} answer={marker}")

    print()
    print("How many times each language was picked (post-assessment, 20 qs):")
    for lang, count in language_counts.items():
        print(f"  {lang:<12} picked {count} times")

    print()
    print("Final memory state:")
    for row in get_user_memory(conn, user_id):
        acc = row["correct_count"] / row["attempts_count"] if row["attempts_count"] else 0
        print(
            f"  {row['language']:<12} skill_score={row['skill_score']:<6} "
            f"attempts={row['attempts_count']:<3} correct={row['correct_count']:<3} "
            f"accuracy={acc:.0%}"
        )

    conn.close()
    print()
    print("Expect: python's skill_score should land high after the assessment and")
    print("barely move; javascript/java/cpp should start low and get picked most")
    print("often in phase 2, since selection weights toward the lowest score.")


if __name__ == "__main__":
    main()