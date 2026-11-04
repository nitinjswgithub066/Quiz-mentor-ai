# ai-engine — Basic Trial (Memory Model Only)

**Status:** v0 trial, built to test one thing in isolation before adding
anything else. This is NOT the full ai-engine yet — no FastAPI, no LLM
calls, no RAG, no ingestion. Just the part that decides what to ask next
and remembers how the user is doing. Everything else gets layered on top
of this once it's trusted.

## What this trial proves

That the adaptive rule from the spec actually works:

- **Trials 1–30**: random language, always beginner difficulty (profiling phase)
- **Trial 31+**: language choice weights toward the user's *weakest*
  languages; difficulty tracks their current level in that language
  (+1 on correct, -1 on wrong, capped 1–10)

Tested by simulating one user who is strong in Python (90% simulated
accuracy) and weak in JS/Java/C++ (20–30%) across 40 trials. Result:

| language | final level | attempts | accuracy |
|---|---|---|---|
| python | 9 | 8 | 100% |
| javascript | 3 | 9 | 44% |
| java | 2 | 14 | 29% |
| cpp | 2 | 9 | 33% |

In the adaptive phase (trial 31–40), Python — already strong — wasn't
selected a single time; the weak languages absorbed all the attention.
That's the intended behavior.

## Why no FastAPI / LLM / RAG yet

Deliberate, not an oversight: this piece (the "memory model") has to be
correct on its own before question-generation logic sits on top of it.
Also practical — this was built and tested in an offline sandbox, so it
only uses Python's standard library (`sqlite3`, `random`) so it could
actually be run and verified rather than handed over untested.

## Files

```
ai-models/
├── app/
│   ├── db/
│   │   └── database.py      # SQLite schema + connection (users, languages, skill_levels, attempts)
│   └── core/
│       └── memory_store.py  # the memory model: read/update skill state, decide next question
├── data/
│   └── quiz_engine.db       # created on first run (not committed)
├── trial_run.py             # simulates 40 trials for one user, prints what the system remembers
└── Development_README.md    # development notes
```

`skill_levels` is the memory: one row per (user, language), tracking
level, attempts, and correct count. `decide_next_question()` reads it to
choose what to ask; `record_attempt()` updates it after every answer.

## How to run it yourself

```bash
cd ai-engine
python3 trial_run.py
```

It resets the DB, simulates 40 trials, and prints the decision made at
key trials plus the final memory state. Re-run anytime — it starts fresh
each time (`reset_db()`).

To inspect the DB directly:

```bash
sqlite3 data/quiz_engine.db "SELECT * FROM skill_levels;"
```

## Known limitations of this trial (on purpose, for now)

- Simulated answers, not real ones — there's no question content yet,
  just the decision loop around a fictional "did they get it right"
  signal.
- Only 4 hardcoded languages. Real version should read languages from
  the DB, allow adding more without code changes.
- Level math is a flat +1/-1. Fine for v1; worth revisiting once there's
  real user data to see if it's too fast/slow.
- No `quiz_sessions` / trial-number tracking across real sessions yet —
  `trial_number` is just passed in by the caller. Needs wiring to
  Firebase-authenticated users and persistent session counts.

## Next steps toward VR1 (mid-December)

1. ✅ Memory model (this trial) — done, tested, working
2. Ingestion pipeline: PDF/link/notes → chunks → embeddings → stored in
   `references` / `reference_chunks` (new tables, not yet built)
3. `llm_client.py`: one hardcoded prompt round-tripping to Claude or
   OpenAI's API successfully (needs network + API key — can't be done
   in this sandbox, needs to run on your machine)
4. `retriever.py`: plug retrieved reference chunks into the prompt (RAG)
5. Wire `decide_next_question()` output + retrieved chunks into an
   actual `/generate-question` FastAPI endpoint
6. Only then: backend orchestration layer, then frontend

Given the mid-December target, steps 2–5 are the real timeline risk —
this trial (step 1) was the cheap, safe part to get right first.
