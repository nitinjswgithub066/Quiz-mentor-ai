"""
quiz_cli.py
-----------
Next test, one level up from trial_run.py: real MCQ content, delivered
one question at a time, scored against YOUR real typed answers, feeding
the same memory model. This is the first end-to-end rehearsal of what
Quiz Mentor actually does at runtime -- the only thing missing is that
the questions come from a hardcoded bank instead of the LLM/RAG pipeline.

Run:
    cd ai-model
    python3 quiz_cli.py
"""

import random

from app.db.database import reset_db, get_connection
from app.core.memory_store import (
    get_or_create_user,
    get_user_memory,
    decide_next_question,
    record_attempt,
)
from app.data.question_bank import QUESTIONS

LANGUAGES = ["python", "java", "c", "html", "css", "javascript"]


def pick_question(language, difficulty, used_ids):
    """Prefer an unused question matching the decided language+difficulty;
    fall back to any unused question if that language is exhausted."""
    candidates = [
        q for q in QUESTIONS
        if q["language"] == language and q["difficulty"] == difficulty and q["id"] not in used_ids
    ]
    if not candidates:
        candidates = [q for q in QUESTIONS if q["id"] not in used_ids]
    return random.choice(candidates) if candidates else None


def ask(question):
    print(f"\n[{question['language'].upper()}] {question['question']}")
    for i, opt in enumerate(question["options"]):
        print(f"  {chr(65 + i)}. {opt}")
    while True:
        raw = input("Your answer (A/B/C/D): ").strip().upper()
        if raw in ("A", "B", "C", "D"):
            return ord(raw) - ord("A")
        print("Please type A, B, C, or D.")


def main():
    reset_db()  # fresh run every time -- see note above
    conn = get_connection()
    user_id = get_or_create_user(conn, firebase_uid="local-test-user", name="You")

    used_ids = set()
    correct_total = 0
    trial = 0

    print("=" * 60)
    print("Quiz Mentor -- 30 question trial (6 languages, profiling phase)")
    print("=" * 60)

    for trial in range(1, 31):
        decision = decide_next_question(conn, user_id, trial, LANGUAGES)
        question = pick_question(decision["language"], decision["difficulty"], used_ids)
        if question is None:
            print("\nQuestion bank exhausted early -- stopping.")
            trial -= 1
            break
        used_ids.add(question["id"])

        print(f"\n--- Question {trial}/30 ({decision['phase']}) ---")
        chosen_index = ask(question)
        is_correct = chosen_index == question["correct_index"]
        print("Correct!" if is_correct else f"Wrong. Correct answer: {chr(65 + question['correct_index'])}.")
        if is_correct:
            correct_total += 1

        record_attempt(
            conn, user_id, question["language"], trial, decision["difficulty"], is_correct
        )

    print("\n" + "=" * 60)
    print(f"Done. {correct_total}/{trial} correct.")
    print("=" * 60)
    print("\nWhat the system now remembers about you:")
    for row in get_user_memory(conn, user_id):
        acc = row["correct_count"] / row["attempts_count"] if row["attempts_count"] else 0
        print(
            f"  {row['language']:<12} level={row['level']:<2} "
            f"attempts={row['attempts_count']:<3} correct={row['correct_count']:<3} "
            f"accuracy={acc:.0%}"
        )
    print("\nAll 30 were in the profiling phase (random language, beginner level),")
    print("same as the spec. Trial 31+ would start weighting toward whichever")
    print("language shows the lowest accuracy above.")

    conn.close()


if __name__ == "__main__":
    main()