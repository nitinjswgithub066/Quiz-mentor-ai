# ai-model — Trial 2: Real Questions, Real Answers (CLI)

**Status:** v0.2 trial. Still no FastAPI, no LLM, no RAG — this step tests
real MCQ content + real human answers flowing through the same memory
model from trial 1, end to end. Everything else (AI-generated questions,
backend, frontend) builds on top of this once it's proven solid.

## What trial 1 tested vs. what this one tests

| | Trial 1 (`trial_run.py`) | Trial 2 (`quiz_cli.py`) |
|---|---|---|
| Questions | simulated (coin-flip per language) | 30 real, hand-written MCQs |
| Answers | randomly generated | typed by you, live |
| Goal | prove the decision/memory logic is correct in isolation | prove the full ask → answer → score → remember loop works with a real person at the keyboard |

This is the first run where the thing you interact with resembles what
Quiz Mentor will actually feel like to use.

## What this trial proves

1. **Real content delivery** — one MCQ at a time, 4 options, clean prompt.
2. **Real answer capture** — reads A/B/C/D from the keyboard, re-asks on
   bad input instead of crashing.
3. **Correct scoring** — checks your answer against the right option and
   tells you immediately if you got it right or what the answer was.
4. **Memory updates in real time** — `skill_levels` updates after every
   single question, not in a batch at the end.
5. **Full language coverage in the profiling window** — all 30 questions
   span 6 languages (python, java, c, html, css, javascript), matching
   the "random beginner question from all languages, trials 1–30" rule
   from the spec.

## Files added since trial 1

ai-model/
├── app/
│ ├── db/
│ │ └── database.py # unchanged from trial 1
│ ├── core/
│ │ └── memory_store.py # unchanged from trial 1
│ └── data/
│ └── question_bank.py # NEW — 30 hardcoded beginner MCQs, 5 per language
├── data/
│ └── quiz_engine.db # created on run
└── quiz_cli.py # NEW — interactive question-by-question loop


`question_bank.py` is a stand-in for AI-generated questions. Each entry
is `{id, language, difficulty, question, options, correct_index}` — the
exact shape a real generated question should land in once the LLM/RAG
pipeline exists, so `quiz_cli.py`'s delivery/scoring logic won't need to
change later, only where the questions come from.

## How to run it

```bash
cd ai-model
python3 quiz_cli.py
```

No venv activation needed, no dependencies — still pure standard library
(`sqlite3`, `random`). Answer honestly, and try being deliberately weak
in one or two languages to sanity-check that the final numbers match
what you'd expect.

At the end it prints your per-language level/accuracy, e.g.: