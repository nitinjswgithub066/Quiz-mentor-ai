"""
quiz_cli.py
-----------
Trial 4: real interactive run of the NEW skill_score pipeline, using
real typed answers throughout.

Two phases:
  1. Mini-assessment -- one real question per language, tier 1 only.
     Tier 2/3 content doesn't exist yet, so this is intentionally
     shallow: it proves the assessment -> skill_score mechanism works
     end to end, not that it calibrates well yet. A real assessment
     needs real tier-2/3 questions, which is separate content work.
  2. Adaptive quiz -- remaining questions from the bank, served via
     decide_next_question()/record_attempt(), weighted toward whatever
     the mini-assessment showed as your weaker languages.

Run:
    cd ai-model
    python3 quiz_cli.py
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
from app.data.question_bank import QUESTIONS

LANGUAGES = ["python", "java", "c", "html", "css", "javascript"]
ADAPTIVE_ROUNDS = 10


def ask(question):
    print(f"\n[{question['language'].upper()}] {question['question']}")
    for i, opt in enumerate(question["options"]):
        print(f"  {chr(65 + i)}. {opt}")
    while True:
        raw = input("Your answer (A/B/C/D): ").strip().upper()
        if raw in ("A", "B", "C", "D"):
            return ord(raw) - ord("A")
        print("Please type A, B, C, or D.")


def pick_question(language, difficulty, used_ids):
    """Prefer an unused question matching language+difficulty; fall
    back to same language any difficulty; fall back to any unused
    question. (The bank is tier-1 only right now, so the fallbacks
    will fire often -- expected until tier 2/3 content exists.)"""
    candidates = [
        q for q in QUESTIONS
        if q["language"] == language and q["difficulty"] == difficulty and q["id"] not in used_ids
    ]
    if not candidates:
        candidates = [q for q in QUESTIONS if q["language"] == language and q["id"] not in used_ids]
    if not candidates:
        candidates = [q for q in QUESTIONS if q["id"] not in used_ids]
    return random.choice(candidates) if candidates else None


def run_mini_assessment(conn, user_id, used_ids):
    print("=" * 60)
    print("PHASE 1: mini-assessment (1 question per language, tier 1 only --")
    print("tier 2/3 content doesn't exist yet, this is a shallow stand-in)")
    print("=" * 60)

    answers_by_language = {}
    for lang in LANGUAGES:
        question = pick_question(lang, 1, used_ids)
        if question is None:
            continue
        used_ids.add(question["id"])
        chosen = ask(question)
        is_correct = chosen == question["correct_index"]
        print("Correct!" if is_correct else f"Wrong. Correct answer: {chr(65 + question['correct_index'])}.")
        answers_by_language[lang] = [{"difficulty": 1, "is_correct": is_correct}]

    scores = score_and_store_assessment(conn, user_id, answers_by_language)
    print("\nInitial skill_scores from the assessment:")
    for lang, score in scores.items():
        print(f"  {lang:<12} {score}")
    return scores


def run_adaptive_quiz(conn, user_id, used_ids):
    print("\n" + "=" * 60)
    print(f"PHASE 2: adaptive quiz ({ADAPTIVE_ROUNDS} questions)")
    print("=" * 60)

    for i in range(1, ADAPTIVE_ROUNDS + 1):
        decision = decide_next_question(conn, user_id, LANGUAGES)
        question = pick_question(decision["language"], decision["difficulty"], used_ids)
        if question is None:
            print("\nQuestion bank exhausted -- stopping early.")
            break
        used_ids.add(question["id"])

        print(f"\n--- Question {i}/{ADAPTIVE_ROUNDS} (difficulty {decision['difficulty']}) ---")
        chosen = ask(question)
        is_correct = chosen == question["correct_index"]
        print("Correct!" if is_correct else f"Wrong. Correct answer: {chr(65 + question['correct_index'])}.")
        # pyrefly: ignore[unexpected-keyword]
        record_attempt(conn, user_id, question["language"], decision["difficulty"], is_correct, source="quiz")


def main():
    reset_db()
    conn = get_connection()
    user_id = get_or_create_user(conn, firebase_uid="local-test-user", name="You")
    used_ids = set()

    run_mini_assessment(conn, user_id, used_ids)
    run_adaptive_quiz(conn, user_id, used_ids)

    print("\n" + "=" * 60)
    print("Final memory state:")
    print("=" * 60)
    for row in get_user_memory(conn, user_id):
        acc = row["correct_count"] / row["attempts_count"] if row["attempts_count"] else 0
        print(
            f"  {row['language']:<12} skill_score={row['skill_score']:<6} "
            f"attempts={row['attempts_count']:<3} correct={row['correct_count']:<3} "
            f"accuracy={acc:.0%}"
        )

    conn.close()


if __name__ == "__main__":
    main()