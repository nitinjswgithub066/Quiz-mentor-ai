"""
memory_store.py
----------------
This is the "memory model" for the trial: it tracks what the system
remembers about each user's ability per language, and decides what to
ask next. No LLM, no RAG here on purpose -- this file has to be correct
and boring before anything AI-generated sits on top of it.

Rule being tested (from your example):
  - trials 1-30:  random language, always beginner difficulty
                   (this is the "profiling" phase)
  - trial 31+:    weight language choice toward the user's WEAKEST
                   languages, and set difficulty from their current
                   level in that language (goes up on a correct streak,
                   down on a wrong streak)
"""

import random
from app.db.database import get_connection

PROFILING_TRIALS = 30
MAX_LEVEL = 10
MIN_LEVEL = 1


def get_or_create_language(conn, name: str) -> int:
    cur = conn.execute("SELECT id FROM languages WHERE name = ?", (name,))
    row = cur.fetchone()
    if row:
        return row["id"]
    cur = conn.execute("INSERT INTO languages (name) VALUES (?)", (name,))
    conn.commit()
    return cur.lastrowid


def get_or_create_user(conn, firebase_uid: str, name: str = "") -> int:
    cur = conn.execute("SELECT id FROM users WHERE firebase_uid = ?", (firebase_uid,))
    row = cur.fetchone()
    if row:
        return row["id"]
    cur = conn.execute(
        "INSERT INTO users (firebase_uid, name) VALUES (?, ?)", (firebase_uid, name)
    )
    conn.commit()
    return cur.lastrowid


def _get_or_create_skill_row(conn, user_id: int, language_id: int):
    cur = conn.execute(
        "SELECT * FROM skill_levels WHERE user_id = ? AND language_id = ?",
        (user_id, language_id),
    )
    row = cur.fetchone()
    if row:
        return row
    conn.execute(
        "INSERT INTO skill_levels (user_id, language_id, level, attempts_count, correct_count) "
        "VALUES (?, ?, 1, 0, 0)",
        (user_id, language_id),
    )
    conn.commit()
    cur = conn.execute(
        "SELECT * FROM skill_levels WHERE user_id = ? AND language_id = ?",
        (user_id, language_id),
    )
    return cur.fetchone()



def get_user_memory(conn, user_id: int) -> list:
    """Everything the system currently remembers about this user."""
    cur = conn.execute(
        """
        SELECT languages.name AS language, skill_levels.level,
               skill_levels.attempts_count, skill_levels.correct_count
        FROM skill_levels
        JOIN languages ON languages.id = skill_levels.language_id
        WHERE skill_levels.user_id = ?
        ORDER BY languages.name
        """,
        (user_id,),
    )
    return [dict(row) for row in cur.fetchall()]


def decide_next_question(conn, user_id: int, trial_number: int, known_languages: list) -> dict:
    """
    Returns {"language": str, "difficulty": int} for the next question,
    following the profiling-then-adaptive rule described above.
    """
    for lang in known_languages:
        get_or_create_language(conn, lang)

    if trial_number <= PROFILING_TRIALS:
        language = random.choice(known_languages)
        return {"language": language, "difficulty": MIN_LEVEL, "phase": "profiling"}

    # Adaptive phase: weight by weakness (fewer correct relative to attempts = weaker)
    weights = []
    for lang in known_languages:
        language_id = get_or_create_language(conn, lang)
        row = _get_or_create_skill_row(conn, user_id, language_id)
        accuracy = (row["correct_count"] / row["attempts_count"]) if row["attempts_count"] else 0
        # lower accuracy -> higher weight to be picked; +0.1 avoids zero weight
        weights.append(max(0.1, 1.0 - accuracy))

    language = random.choices(known_languages, weights=weights, k=1)[0]
    language_id = get_or_create_language(conn, language)
    row = _get_or_create_skill_row(conn, user_id, language_id)
    return {"language": language, "difficulty": row["level"], "phase": "adaptive"}


def record_attempt(conn, user_id: int, language: str, trial_number: int, difficulty: int, is_correct: bool):
    """Update memory after one answered question."""
    language_id = get_or_create_language(conn, language)
    row = _get_or_create_skill_row(conn, user_id, language_id)

    new_level = row["level"]
    if is_correct and new_level < MAX_LEVEL:
        new_level += 1
    elif not is_correct and new_level > MIN_LEVEL:
        new_level -= 1

    conn.execute(
        """
        UPDATE skill_levels
        SET attempts_count = attempts_count + 1,
            correct_count = correct_count + ?,
            level = ?,
            last_updated = CURRENT_TIMESTAMP
        WHERE user_id = ? AND language_id = ?
        """,
        (1 if is_correct else 0, new_level, user_id, language_id),
    )
    conn.execute(
        "INSERT INTO attempts (user_id, language_id, trial_number, difficulty, is_correct) "
        "VALUES (?, ?, ?, ?, ?)",
        (user_id, language_id, trial_number, difficulty, 1 if is_correct else 0),
    )
    conn.commit()
