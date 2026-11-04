"""
assessment.py
-------------
Scores the one-time onboarding assessment and writes the result as
each language's starting skill_score. Doesn't handle delivering the
assessment (timer, question selection) -- just the scoring math.
"""

from app.core.m_memory_store import set_initial_score

DIFFICULTY_WEIGHT = {1: 1, 2: 2, 3: 3}  # harder questions count for more


def score_assessment(answers: list) -> float:
    """
    answers: list of {"difficulty": 1|2|3, "is_correct": bool}
    Include unanswered questions as is_correct=False (that's what a
    timeout auto-submit means).
    Returns a 0-100 score.
    """
    possible = sum(DIFFICULTY_WEIGHT[a["difficulty"]] for a in answers)
    if possible == 0:
        return 0.0
    earned = sum(DIFFICULTY_WEIGHT[a["difficulty"]] for a in answers if a["is_correct"])
    return round((earned / possible) * 100, 1)


def score_and_store_assessment(conn, user_id: int, answers_by_language: dict):
    """
    answers_by_language: {"python": [{"difficulty":1,"is_correct":True}, ...], ...}
    Scores each language's answers separately and writes the initial
    skill_score for each.
    """
    results = {}
    for language, answers in answers_by_language.items():
        score = score_assessment(answers)
        set_initial_score(conn, user_id, language, score)
        results[language] = score
    return results  