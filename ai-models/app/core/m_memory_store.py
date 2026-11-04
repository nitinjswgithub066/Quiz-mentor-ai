"""
memory_store.py
----------------
Memory model, updated: ability is a continuous skill_score (0-100) per
(user, language), not a discrete level. No profiling-phase branching
here anymore either -- the assessment (assessment.py) does that job
once at onboarding, so live quizzes are adaptive from the first
question.
"""

import random
from app.db.m_database import get_connection

MIN_SCORE = 0.0
MAX_SCORE = 100.0
EMA_ALPHA = 0.2  # how much each new answer moves the score


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
        "INSERT INTO skill_levels (user_id, language_id, skill_score, assessed, "
        "attempts_count, correct_count) VALUES (?, ?, 0.0, 0, 0, 0)",
        (user_id, language_id),
    )
    conn.commit()
    cur = conn.execute(
        "SELECT * FROM skill_levels WHERE user_id = ? AND language_id = ?",
        (user_id, language_id),
    )
    return cur.fetchone()


def score_to_difficulty(score: float) -> int:
    """0-33 -> 1 (basic), 34-66 -> 2 (intermediate), 67-100 -> 3 (advanced)."""
    if score < 34:
        return 1
    elif score < 67:
        return 2
    return 3


def get_user_memory(conn, user_id: int) -> list:
    cur = conn.execute(
        """
        SELECT languages.name AS language, skill_levels.skill_score,
               skill_levels.assessed, skill_levels.attempts_count,
               skill_levels.correct_count
        FROM skill_levels
        JOIN languages ON languages.id = skill_levels.language_id
        WHERE skill_levels.user_id = ?
        ORDER BY languages.name
        """,
        (user_id,),
    )
    return [dict(row) for row in cur.fetchall()]


def set_initial_score(conn, user_id: int, language: str, score: float):
    """Called once, right after the assessment is scored."""
    language_id = get_or_create_language(conn, language)
    _get_or_create_skill_row(conn, user_id, language_id)
    conn.execute(
        """
        UPDATE skill_levels
        SET skill_score = ?, assessed = 1, last_updated = CURRENT_TIMESTAMP
        WHERE user_id = ? AND language_id = ?
        """,
        (round(score, 1), user_id, language_id),
    )
    conn.commit()


def decide_next_question(conn, user_id: int, known_languages: list) -> dict:
    """
    No trial_number, no profiling phase -- always weights toward the
    user's weakest languages, same as the old trial 31+ behavior, but
    from question 1, since the assessment already calibrated them.
    """
    weights = []
    for lang in known_languages:
        language_id = get_or_create_language(conn, lang)
        row = _get_or_create_skill_row(conn, user_id, language_id)
        # lower score -> higher weight to be picked; floor avoids zero weight
        weights.append(max(0.1, 1.0 - (row["skill_score"] / 100.0)))

    language = random.choices(known_languages, weights=weights, k=1)[0]
    language_id = get_or_create_language(conn, language)
    row = _get_or_create_skill_row(conn, user_id, language_id)
    return {"language": language, "difficulty": score_to_difficulty(row["skill_score"])}


def record_attempt(conn, user_id: int, language: str, difficulty: int, is_correct: bool, source: str = "quiz"):
    """Update memory after one answered question, via EMA instead of +-1."""
    language_id = get_or_create_language(conn, language)
    row = _get_or_create_skill_row(conn, user_id, language_id)

    outcome = 100.0 if is_correct else 0.0
    new_score = row["skill_score"] + EMA_ALPHA * (outcome - row["skill_score"])
    new_score = max(MIN_SCORE, min(MAX_SCORE, round(new_score, 1)))

    conn.execute(
        """
        UPDATE skill_levels
        SET attempts_count = attempts_count + 1,
            correct_count = correct_count + ?,
            skill_score = ?,
            last_updated = CURRENT_TIMESTAMP
        WHERE user_id = ? AND language_id = ?
        """,
        (1 if is_correct else 0, new_score, user_id, language_id),
    )
    conn.execute(
        "INSERT INTO attempts (user_id, language_id, source, difficulty, is_correct) "
        "VALUES (?, ?, ?, ?, ?)",
        (user_id, language_id, source, difficulty, 1 if is_correct else 0),
    )
    conn.commit()